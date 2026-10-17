"""Parabolic SAR crosses with an EMA 2, RSI 6 and ADX 30 filter and an ATR bracket, broker days: the close crossing
above the SAR with the close above its EMA 2, RSI 6 > 60 and ADX >= 30 goes long; the mirror (RSI < 40) goes short;
each trade has a stop 1.5 ATR away and a target 3 ATR away.
Port of FMZ strategy #491897 "多因子趋势追踪量化策略-Multi-Factor-Trend-Following-Quantitative-Strategy" (Estrategia SAR+EMA+RSI con Alertas).

FMZ source id: 491897

Source
    https://www.fmz.com/strategy/491897 (PineScript v5, FMZ last modified 2025-04-24 17:23:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 110-168), SAR 0.02 / 0.02 / 0.2, EMA 2, RSI 6, DMI 14 / 14, ADX >= 30, ATR 14 x 1.5
    long = crossover(close, sar) and close > ema2 and rsi > 60 and adx >= 30
    short = crossunder(close, sar) and close < ema2 and rsi < 40 and adx >= 30
    on entry: exit(stop = close -+ 1.5 x ATR, limit = close +- 3 x ATR), levels from the signal bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.sar as TradingView documents it (as #428699); ta.dmi(14, 14) with Wilder smoothing and fixnan (as #426579).
    * The bracket is placed once, on the signal bar, from that bar's close and ATR: sl_stop = 1.5 x ATR / close,
      tp_stop = 2 x that, shifted one bar inside stops() and re-based on the fill price (house rule).
    * The alerts and the risk-based quantity are not signals (quantity quoted in original_sizing.txt).
    * Entries reverse (REVERSAL INTENDED); a long and a short cannot fall on one bar (the close cannot cross the SAR
      both ways).
    * Stop module: portfolio_kwargs {} (driver D4). Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, SAR, oscillators and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 2 %-risk quantity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_491897_sar_ema_rsi_adx_bracket"
FAMILY = "parabolic_sar"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_threshold": [30, 20],
    "atr_mult": [1.5, 2.5],
}
DEFAULT_PARAMS = {"sar_start": 0.02, "sar_inc": 0.02, "sar_max": 0.2, "rsi_len": 6, "ema_fast": 2,
                  "adx_threshold": 30, "atr_mult": 1.5, "rr": 2.0, "rsi_long": 60, "rsi_short": 40}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _adx_pine(bars, di_len, adx_len):
    """Pine's built-in-style dirmov/adx: RMA smoothing, fixnan on DI+/DI-."""
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = np.where(up.isna(), np.nan, np.where((up > down) & (up > 0), up, 0.0))
    minus_dm = np.where(down.isna(), np.nan, np.where((down > up) & (down > 0), down, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trs = _rma(tr, di_len)
    plus = _fixnan((100 * _rma(pd.Series(plus_dm, index=h.index), di_len) / trs).to_numpy())
    minus = _fixnan((100 * _rma(pd.Series(minus_dm, index=h.index), di_len) / trs).to_numpy())
    s = plus + minus
    dx = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1, s), index=h.index)
    return pd.Series(plus, index=h.index), pd.Series(minus, index=h.index), 100 * _rma(dx, adx_len)


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar): starts on bar 1, direction from close vs
    the previous close; value capped by the previous two bars' lows (highs)."""
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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sar = _sar_pine(bars_df, p["sar_start"], p["sar_inc"], p["sar_max"])
    ema = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    _, _, adx = _adx_pine(bars_df, 14, 14)
    up = (c > sar) & (c.shift(1) <= sar.shift(1))
    dn = (c < sar) & (c.shift(1) >= sar.shift(1))
    long_e = (up & (c > ema) & (rsi > p["rsi_long"]) & (adx >= p["adx_threshold"])).astype(bool)
    short_e = (dn & (c < ema) & (rsi < p["rsi_short"]) & (adx >= p["adx_threshold"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    dist = p["atr_mult"] * _atr(bars_df, 14) / bars_df["close"]
    return {"sl_stop": dist.shift(1), "tp_stop": (p["rr"] * dist).shift(1)}


def portfolio_kwargs(**params):
    return {}
