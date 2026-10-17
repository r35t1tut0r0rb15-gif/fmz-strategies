"""HPotter combo, 1-hour bars: the 123 reversal and the fractal chaos oscillator state (+1 when a new up fractal forms, -1
on a new down fractal) must agree; both long holds a long, both short holds a short, any disagreement closes everything.
Port of FMZ strategy #430887 "Combo Strategy of 123 Reversal and Fractal Chaos Oscillator" (Combo Backtest 123 Reversal & Fractal Chaos Oscillator).

FMZ source id: 430887

Source
    https://www.fmz.com/strategy/430887 (PineScript v4, FMZ last modified 2023-11-02 16:43:41).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 171-262), 123 reversal stoch 15 / 1 / 3, level 50; FCO pattern 1
    posReversal123: close[2] < close[1] < close and K < D and K > 50 -> 1; mirror -> -1; else hold
    fractalUp(1): high[2] when high[1] < high[2] and high[3] < high[2], else the last one (fractalDn mirrored)
    posFCO = 1 when fractalUp changed, -1 when fractalDn changed, else hold
    both 1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The fractal is confirmed on the bar after its right side (high[pattern + 1] with pattern bars
      on each side), so it uses completed bars only. When both fractals change on one bar the up one
      wins, as written. "Trade reverse" defaults to false and is fixed.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a stochastic and fractal states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG430887 (2 members, best partner #439996, Jaccard 0.816); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430887_combo_123_fractal_chaos"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [15, 30],
    "pattern": [1, 2],
}
DEFAULT_PARAMS = {"length": 15, "k_smoothing": 1, "d_length": 3, "level": 50, "pattern": 1}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _hold(cond_up, cond_dn):
    m = len(cond_up)
    out = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if cond_up[i]:
            q = 1
        elif cond_dn[i]:
            q = -1
        out[i] = q
    return out


def _fractal(x, pat, up):
    """fractalUp / fractalDn as written: x[pat + 1] when the pat bars on each side are lower (higher)."""
    m = len(x)
    out = np.zeros(m)
    res = 0.0
    for i in range(m):
        if i >= 2 * pat + 1:
            okl = all((x[i - j] < x[i - j - 1]) if up else (x[i - j] > x[i - j - 1]) for j in range(1, pat + 1))
            okr = all((x[i - j] < x[i - j + 1]) if up else (x[i - j] > x[i - j + 1])
                      for j in range(pat + 2, 2 * pat + 2))
            if okl and okr:
                res = x[i - pat - 1]
        out[i] = res
    return out


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
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    pos1 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())
    pat = int(p["pattern"])
    fu = _fractal(h.to_numpy(dtype=float), pat, True)
    fd = _fractal(lo.to_numpy(dtype=float), pat, False)
    chu = np.concatenate(([False], fu[1:] != fu[:-1]))
    chd = np.concatenate(([False], fd[1:] != fd[:-1]))
    pos2 = _hold(chu, chd)
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
