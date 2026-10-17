"""Smoothed-candle colour changes with a small fixed bracket, two-day bars: when the Heikin-Ashi-style candle (close =
ohlc4, open = average of the previous smoothed open and close) turns from red to green by more than 1 % of its range
the strategy goes long; green to red goes short; each trade has a 20-tick stop and a 40-tick target (as ATR
multiples).
Port of FMZ strategy #484096 "动态色彩阈值波动分析交易策略-Dynamic-Color-Threshold-Volatility-Analysis-Trading-Strategy" (Color Code Overlay Strategy).

FMZ source id: 484096

Source
    https://www.fmz.com/strategy/484096 (PineScript v5, FMZ last modified 2025-02-28 09:59:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 254-332), trade type Both, SL 20 / TP 40 pips (x mintick)
    cc_close = ohlc4;  cc_open = na(prev) ? (open + close) / 2 : (cc_open[1] + cc_close[1]) / 2
    threshold = 1 % of (max(high, cc_open, cc_close) - min(low, cc_open, cc_close))
    red -> green with |cc_close - cc_open| > threshold -> entry long + exit(stop = close - 20 ticks, limit = close + 40
    ticks), close short;  green -> red -> close long, entry short (mirrored bracket)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: on the author's 2-day ETH_USDT (tick 0.01, 2-day ATR about 200) 20 / 40 ticks are about 0.001 /
      0.002 Wilder ATR(14) (judgement before any backtest): sl_stop = sl_atr x ATR / close of the signal bar, tp_stop =
      2 x that, shifted one bar inside stops() and re-based on the fill. A colour change below the threshold emits
      nothing, so the next one can repeat the side while held and re-place the bracket: mark trailing_stop_pending;
      the port keeps the entry's bracket.
    * Closes act on the position held at the bar's start (#430850); entries reverse (REVERSAL INTENDED). The trade-type
      input is a GRID variant.
    * Stop module: portfolio_kwargs {} (D4). Two-day bars are blocks of broker-day dates from 1970-01-01 (decision
      owed, as #426509); FREQ = "2D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar (re-placement marked).
    2 generic: ADAPT, tick distances -> ATR multiples; smoothed candles.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in two-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484096_smoothed_candle_colour_flip"
FAMILY = "heikin_ashi"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.001, 1.0],
    "trade_type": ["Both", "Long Only"],
}
DEFAULT_PARAMS = {"trade_type": "Both", "sl_atr": 0.001, "tp_ratio": 2.0, "threshold_pct": 1.0, "atr_len": 14}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    m = len(c)
    cc_c = (o + h + lo + c) / 4
    cc_o = np.empty(m)
    for i in range(m):
        cc_o[i] = (o[i] + c[i]) / 2 if i == 0 else (cc_o[i - 1] + cc_c[i - 1]) / 2
    cc_h = np.maximum(h, np.maximum(cc_o, cc_c))
    cc_l = np.minimum(lo, np.minimum(cc_o, cc_c))
    thr = p["threshold_pct"] / 100 * (cc_h - cc_l)
    bull = cc_c > cc_o
    was = np.concatenate(([False], bull[:-1]))
    big = np.abs(cc_c - cc_o) > thr
    g2r = was & ~bull & big
    r2g = ~was & bull & big
    r2g[0] = g2r[0] = False                              # no previous smoothed candle on the first bar
    longs = p["trade_type"] in ("Both", "Long Only")
    shorts = p["trade_type"] in ("Both", "Short Only")
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if longs:
            if r2g[i]:
                pos = 1
            if g2r[i] and start == 1 and pos == 1:
                pos = 0
        if shorts:
            if g2r[i]:
                pos = -1
            if r2g[i] and start == -1 and pos == -1:
                pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["sl_atr"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["tp_ratio"] * sl}


def portfolio_kwargs(**params):
    return {}
