"""MACD, Parabolic SAR and SuperTrend agreement with a SAR close exit, two-day bars: when the MACD (13 / 27 / 9) is
above its signal, the close is above the SAR and the SuperTrend (11, 3) is up, the strategy goes long; when all three
are bearish it goes short; a close on the wrong side of the SAR closes the trade.
Port of FMZ strategy #488537 "Vishal-自适应多指标交易策略-Vishal-Adaptive-Multi-Indicator-Trading-Strategy" (Vishal Strategy).

FMZ source id: 488537

Source
    https://www.fmz.com/strategy/488537 (PineScript v6, FMZ last modified 2025-03-28 17:17:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 118-192), MACD 13 / 27 / 9, SuperTrend 11 x 3, SAR 0.02 / 0.02 / 0.2
    flags keep the last state of macd vs signal, close vs SAR and the SuperTrend direction (direction < 0 = up)
    long = all three bullish -> entry long;  short = all three bearish -> entry short
    long held and close < sar -> close long;  short held and close > sar -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend and ta.sar as Pine defines them (as #488901 / #428699). A long signal needs the close above the
      SAR, so the SAR exit cannot fire on a long-signal bar; a short signal on a long bar reverses anyway.
    * Every condition bar is an entry; entries reverse (REVERSAL INTENDED). Exits are close-based.
    * FREQ = "2D" from the backtest header (period 2d): two-day bars from broker days in fixed blocks counted from
      1970-01-01 (block phase: decision owed), as #426509.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD, SAR and SuperTrend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity percentage quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488537_macd_sar_supertrend_agreement"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "st_factor": [3.0, 2.0],
    "sar_max": [0.2, 0.1],
}
DEFAULT_PARAMS = {"fast": 13, "slow": 27, "signal": 9, "st_len": 11, "st_factor": 3.0, "sar_step": 0.02,
                  "sar_max": 0.2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=2):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _pine_st_direction(bars_df, factor, n):
    """ta.supertrend direction: 1 = down-trend, -1 = up-trend; 0 before the ATR exists."""
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr(bars_df, n).to_numpy(dtype=float)
    src = (h + lo) / 2
    m = len(c)
    d_out = np.zeros(m, dtype=np.int8)
    pu = pl = 0.0
    prev_st = np.nan
    for i in range(m):
        if np.isnan(atr[i]):
            pu = pl = 0.0
            continue
        up, lw = src[i] + factor * atr[i], src[i] - factor * atr[i]
        if i > 0:
            lw = lw if (lw > pl or c[i - 1] < pl) else pl
            up = up if (up < pu or c[i - 1] > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif prev_st == pu:
            d = -1 if c[i] > up else 1
        else:
            d = 1 if c[i] < lw else -1
        prev_st = lw if d == -1 else up
        pu, pl = up, lw
        d_out[i] = d
    return d_out


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar), as #428699."""
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    out = np.full(m, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, m):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below and h[i] > max_min:
                max_min, acc = h[i], min(acc + inc, maximum)
            elif (not below) and lo[i] < max_min:
                max_min, acc = lo[i], min(acc + inc, maximum)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return pd.Series(out, index=bars.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def _flag(on, off):
    out = np.zeros(len(on), dtype=bool)
    cur = False
    for i in range(len(on)):
        if on[i]:
            cur = True
        if off[i]:
            cur = False
        out[i] = cur
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    sar = _sar_pine(bars_df, p["sar_step"], p["sar_step"], p["sar_max"])
    d = _pine_st_direction(bars_df, float(p["st_factor"]), int(p["st_len"]))
    m_f = _flag((macd > sig).to_numpy(), (macd < sig).to_numpy())
    s_f = _flag((c > sar).to_numpy(), (c < sar).to_numpy())
    t_f = _flag(d < 0, d > 0)
    long_e = pd.Series(m_f & s_f & t_f, index=c.index)
    short_e = pd.Series(~m_f & ~s_f & ~t_f, index=c.index)
    long_x = ((c < sar) & ~short_e).astype(bool)
    short_x = ((c > sar) & ~long_e).astype(bool)
    return long_e, long_x, short_e, short_x


def portfolio_kwargs(**params):
    return {}
