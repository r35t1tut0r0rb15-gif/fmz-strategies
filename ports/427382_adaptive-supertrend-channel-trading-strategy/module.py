"""SuperTrend cloud, long only: two SuperTrend lines (3 x ATR 10 and 6 x ATR 10); the close crossing
above one while already above the other goes long; a close below either line closes the long.
Port of FMZ strategy #427382 "Adaptive Supertrend Channel Trading Strategy".

FMZ source id: 427382

Source
    https://www.fmz.com/strategy/427382 (PineScript v4, FMZ last modified 2023-09-20 15:17:51).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 164-234), multiplier 3, period 10, self-adjusting off
    up_k = hl2 - m_k atr(10); up_trend_k = close[1] > up_trend_k[1] ? max(up_k, up_trend_k[1]) : up_k (down mirrors)
    trend_k = close > down_trend_k[1] ? 1 : close < up_trend_k[1] ? -1 : trend_k[1]; st_k = line of trend_k
    buy = crossover(close, st1) and close > st2 or crossover(close, st2) and close > st1 -> entry long
    close < st1 or close < st2 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The self-adjusting multiplier (stdev / close based) is off by default; the grid tries it.
    * `up_trend = 0.0` with an explicit [1]: the previous bar's line (0 before the first bar), as written.
    * time_cond is the constant true. Long only; entries only from flat; one signal per bar.
    * FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, initial capital stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427382_supertrend_cloud_long"
FAMILY = "supertrend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "multi": [3.0, 2.0],
    "period": [10, 20],
    "self_adjust": [False, True],
}
DEFAULT_PARAMS = {"multi": 3.0, "period": 10, "self_adjust": False}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def _line(cv, hl2, atr, mult):
    m = len(cv)
    ut, dt = np.zeros(m), np.zeros(m)
    st = np.full(m, np.nan)
    trend = 1
    for i in range(m):
        up_l, dn_l = hl2[i] - mult[i] * atr[i], hl2[i] + mult[i] * atr[i]
        u1 = ut[i - 1] if i else 0.0
        d1 = dt[i - 1] if i else 0.0
        c1 = cv[i - 1] if i else np.nan
        ut[i] = max(up_l, u1) if c1 > u1 else up_l
        dt[i] = min(dn_l, d1) if c1 < d1 else dn_l
        if cv[i] > d1:
            trend = 1
        elif cv[i] < u1:
            trend = -1
        st[i] = ut[i] if trend == 1 else dt[i]
    return st


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["period"])
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, n).to_numpy()
    mult = np.full(len(c), float(p["multi"]))
    if bool(p["self_adjust"]):
        mult = mult * ((c.rolling(n).std(ddof=0) / c) * 100 + 1).to_numpy()
    cv, hl2 = c.to_numpy(dtype=float), ((h + lo) / 2).to_numpy()
    st1 = _line(cv, hl2, atr, mult)
    st2 = _line(cv, hl2, atr, 2 * mult)
    c1 = np.concatenate(([np.nan], cv[:-1]))
    s11 = np.concatenate(([np.nan], st1[:-1]))
    s21 = np.concatenate(([np.nan], st2[:-1]))
    buy = ((cv > st1) & (c1 <= s11) & (cv > st2)) | ((cv > st2) & (c1 <= s21) & (cv > st1))
    out = (cv < st1) | (cv < st2)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and buy[i]:
            le[i], pos = True, 1
        elif pos == 1 and out[i]:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
