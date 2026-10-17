"""HPotter's Ehlers Fisher transform state, 1-hour bars: the Fisher transform of the hl2 position in its 10-bar range above
zero turns the state long, below zero short; always in.
Port of FMZ strategy #434166 "Fisher变换指标回测策略Fisher-Transform-Backtest-Strategy" (Fisher Transform Indicator by Ehlers Backtest).

FMZ source id: 434166

Source
    https://www.fmz.com/strategy/434166 (PineScript v2, FMZ last modified 2023-12-04 13:43:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 187-205), length 10, reverse false
    v1 = 0.66 ((hl2 - min) / (max - min) - 0.5) + 0.67 nz(v1[1]);  v2 = clamp(v1, -0.999, 0.999)
    fish = 0.5 log((1 + v2) / (1 - v2)) + 0.5 nz(fish[1]);  pos = fish > 0 ? 1 : fish < 0 ? -1 : pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * The recursions start from 0 (nz), as written; the clamp is at +/- 0.99 -> 0.999.
    * strategy.entry reverses: REVERSAL INTENDED. reverse is false. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a bounded transform of the range position.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: DG434166 (3 members, best partner #439975, Jaccard 0.937); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434166_fisher_transform_state"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20, 40],
}
DEFAULT_PARAMS = {"length": 10}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hl2 = (bars_df["high"] + bars_df["low"]) / 2
    n = int(p["length"])
    mx, mn = hl2.rolling(n).max().to_numpy(), hl2.rolling(n).min().to_numpy()
    x = hl2.to_numpy(dtype=float)
    m = len(x)
    tgt = np.zeros(m, dtype=np.int8)
    v1 = fish = 0.0
    pos = 0
    for i in range(m):
        rng = mx[i] - mn[i]
        raw = (x[i] - mn[i]) / rng - 0.5 if rng and not np.isnan(rng) else np.nan
        nv1 = 0.33 * 2 * raw + 0.67 * v1
        v1 = 0.0 if np.isnan(nv1) else nv1
        v2 = 0.999 if nv1 > 0.99 else (-0.999 if nv1 < -0.99 else nv1)
        nf = 0.5 * np.log((1 + v2) / (1 - v2)) + 0.5 * fish if not np.isnan(v2) else np.nan
        fish = 0.0 if np.isnan(nf) else nf
        if nf > 0:
            pos = 1
        elif nf < 0:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
