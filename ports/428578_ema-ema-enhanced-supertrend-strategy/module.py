"""SuperTrend flip, 6-hour bars: the trend turning up (close above the ratcheted 3 x ATR 10 band) goes
long, turning down goes short.
Port of FMZ strategy #428578 "EMA Enhanced SuperTrend Strategy" (SuperTrend STRATEGY).

FMZ source id: 428578

Source
    https://www.fmz.com/strategy/428578 (PineScript v4, FMZ last modified 2023-10-07 10:07:15).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 262-313), ATR 10 (Wilder), multiplier 3, source hl2
    up = hl2 - 3 atr; up1 = nz(up[1], up); up := close[1] > up1 ? max(up, up1) : up (dn mirrors)
    trend := trend == -1 and close > dn1 ? 1 : trend == 1 and close < up1 ? -1 : trend (from 1)
    trend flips to 1 -> entry long; flips to -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Change ATR Calculation Method" is on (default): Wilder ATR. The EMA 305 appended after a
      second //@version=3 line is drawn only. The date window is open.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "6h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR multiples only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG428578 (4 members, best partner #428613, Jaccard 0.882) and ND427399; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428578_supertrend_flip_6h"
FAMILY = "supertrend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "6h"  # backtest header period: 6h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "periods": [10, 14],
    "multiplier": [3.0, 2.0],
}
DEFAULT_PARAMS = {"periods": 10, "multiplier": 3.0}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["periods"])).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    k = float(p["multiplier"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    up_p = dn_p = np.nan
    trend, pos = 1, 0
    for i in range(m):
        up, dn = src[i] - k * atr[i], src[i] + k * atr[i]
        up1 = up if np.isnan(up_p) else up_p
        dn1 = dn if np.isnan(dn_p) else dn_p
        c1 = cv[i - 1] if i else np.nan
        if c1 > up1:
            up = max(up, up1)
        if c1 < dn1:
            dn = min(dn, dn1)
        prev_t = trend
        if trend == -1 and cv[i] > dn1:
            trend = 1
        elif trend == 1 and cv[i] < up1:
            trend = -1
        if trend == 1 and prev_t == -1:
            pos = 1
        elif trend == -1 and prev_t == 1:
            pos = -1
        tgt[i] = pos
        up_p, dn_p = up, dn
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
