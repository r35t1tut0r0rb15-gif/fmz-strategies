"""SMA 200 side with a classic SuperTrend (14, 3) state, 3-hour bars: every bar closing above the SMA 200 in a SuperTrend
up-trend is a long entry, below it in a down-trend a short entry; a long closes when the SuperTrend turns down (shorts
mirrored).
Port of FMZ strategy #488023 "长期趋势与波动率识别相结合的指数移动均线超级趋势量化交易策略-Long-term-Trend-and-Volatility-Recognition-Combined-Exponential-Moving-Average-SuperTrend-Quantitative-Trading-Strategy" (Moving Average + SuperTrend Strategy).

FMZ source id: 488023

Source
    https://www.fmz.com/strategy/488023 (PineScript v6, FMZ last modified 2025-03-24 14:42:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 202-243), SMA 200, SuperTrend factor 3, ATR 14
    trendUp = close[1] > trendUp[1] ? max(hl2 - 3 ATR, trendUp[1]) : hl2 - 3 ATR (trendDown mirrored)
    trend = close > trendDown[1] ? 1 : close < trendUp[1] ? -1 : nz(trend[1], 1)
    close > sma and trend == 1 -> entry long;  close < sma and trend == -1 -> entry short
    position_size > 0 and trend == -1 -> close long;  position_size < 0 and trend == 1 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SuperTrend recursion as written (na history compares false; the first trend is 1).
    * The closes test the position held at the bar's start and never undo an entry on that bar (#430850); a short
      signal while long reverses. REVERSAL INTENDED.
    * FREQ = "3h" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a moving average and an ATR band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_488023_sma200_classic_supertrend"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "ma_length": [200, 100],
}
DEFAULT_PARAMS = {"ma_length": 200, "factor": 3.0, "period": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _trend(bars_df, factor, n):
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr(bars_df, n).to_numpy(dtype=float)
    hl = (h + lo) / 2
    m = len(c)
    out = np.ones(m, dtype=np.int8)
    tu_p = td_p = np.nan
    tr_p = 1
    for i in range(m):
        up, dn = hl[i] - factor * atr[i], hl[i] + factor * atr[i]
        c1 = c[i - 1] if i > 0 else np.nan
        tu = max(up, tu_p) if c1 > tu_p else up            # NaN comparisons are False, as Pine's na
        td = min(dn, td_p) if c1 < td_p else dn
        if c[i] > td_p:
            t = 1
        elif c[i] < tu_p:
            t = -1
        else:
            t = tr_p
        out[i] = t
        tu_p, td_p, tr_p = tu, td, t
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ma = c.rolling(int(p["ma_length"])).mean()
    t = _trend(bars_df, float(p["factor"]), int(p["period"]))
    go_l = ((c > ma).to_numpy()) & (t == 1)
    go_s = ((c < ma).to_numpy()) & (t == -1)
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if go_l[i]:
            pos = 1
        if go_s[i]:
            pos = -1
        if start == 1 and t[i] == -1 and pos == 1:
            pos = 0
        if start == -1 and t[i] == 1 and pos == -1:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
