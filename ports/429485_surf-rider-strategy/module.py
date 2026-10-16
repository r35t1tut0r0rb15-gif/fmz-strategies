"""HPotter combo, hourly bars: the 123 reversal and Blau's Ergodic Candlestick Oscillator must agree; both long
holds a long, both short holds a short, any disagreement closes everything.
Port of FMZ strategy #429485 "Surf Rider Strategy" (Combo Backtest 123 Reversal & ECO Strategy).

FMZ source id: 429485

Source
    https://www.fmz.com/strategy/429485 (PineScript v4, FMZ last modified 2023-10-17 15:30:18).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 207-246), stochastic 14 / 1 / 3, level 50; ECO 32 / 12
    123: close[2] < close[1] and close > close[1] and K < D and K > 50 -> 1; mirror -> -1; else pos[1]
    ECO = 100 x ema(ema(close - open, 32), 12) / ema(ema(high - low, 32), 12); > 0 -> 1; <= 0 -> -1
    both 1 -> entry long; both -1 -> entry short; otherwise strategy.close_all()

Interpretation choices (Pine rules in SURVEY_README.md)
    * An na ECO keeps the previous state. "Trade reverse" defaults to false and is fixed.
    * A one-bar change from long to short reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and a dimensionless ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #432231, Jaccard 0.664); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429485_combo_123_eco"
FAMILY = "combo_123_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "r": [32, 16],
    "s": [12, 6],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "r": 32, "s": 12}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    pos1 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())
    ee = lambda x: x.ewm(span=int(p["r"]), adjust=False).mean().ewm(span=int(p["s"]), adjust=False).mean()  # noqa: E731
    eco = 100 * ee(c - o) / ee(h - lo).replace(0.0, np.nan)
    pos2 = _hold((eco > 0).to_numpy(), (eco <= 0).to_numpy())
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
