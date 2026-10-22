"""SuperTrend 10 / 3 flips with the EMA 9 / 15 side, 2-minute bars: a flip up with the EMA 9 over the EMA 15 goes long; a flip down with it under goes short (closing the long); any up-trend bar closes a short.
Port of FMZ strategy #489297 "基于EMA和Supertrend结合的多时间框架趋势跟踪策略-Multi-timeframe-Trend-Following-Strategy-Based-on-EMA-and-Supertrend-Combination" (Supertrend Strategy for Renko).

FMZ source id: 489297

Source
    https://www.fmz.com/strategy/489297 (PineScript v6, FMZ last modified 2025-04-03 11:23:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 176-235), EMA 9 / 15 / 15; SuperTrend ATR 10 x 3 (ta.atr), hl2; 100 % of equity
    up / dn bands ratcheted on close[1];  trend flips up when close > dn1, down when close < up1
    trend flips up and ema9 > ema15 -> entry Long;  flips down and ema9 < ema15 -> close Long, entry Short;  trend == 1 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bands and trend follow the script's own recursion, in a loop. A flip down without the EMA side
      keeps the long; the short closes on every up-trend bar. The short entry reverses the long (REVERSAL
      INTENDED). FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend flips with an EMA side filter.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489297_supertrend10_3_flip_ema9_15_side_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "Multiplier": [3.0, 2.0],
    "Periods": [10, 20],
}
DEFAULT_PARAMS = {"Multiplier": 3.0, "Periods": 10, "fast": 9, "slow": 15}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["Periods"])).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    k = float(p["Multiplier"])
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    up, dn, tv = np.full(m, np.nan), np.full(m, np.nan), np.ones(m)
    t = 1
    for i in range(m):
        ru, rd = src[i] - k * atr[i], src[i] + k * atr[i]
        u1 = up[i - 1] if i >= 1 and not np.isnan(up[i - 1]) else ru
        d1 = dn[i - 1] if i >= 1 and not np.isnan(dn[i - 1]) else rd
        c1 = cv[i - 1] if i >= 1 else np.nan
        up[i] = max(ru, u1) if c1 > u1 else ru
        dn[i] = min(rd, d1) if c1 < d1 else rd
        if t == -1 and cv[i] > d1:
            t = 1
        elif t == 1 and cv[i] < u1:
            t = -1
        tv[i] = t
    trend = pd.Series(tv, index=c.index)
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (trend == 1) & (trend.shift(1) == -1) & (ef > es)
    se = (trend == -1) & (trend.shift(1) == 1) & (ef < es)
    sx = (trend == 1) & ~le
    false = pd.Series(False, index=c.index)
    return le, false, se, sx


def portfolio_kwargs(**params):
    return {}
