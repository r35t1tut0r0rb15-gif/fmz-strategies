"""HPotter combo, 15-minute bars: the 123 reversal and Blau's ergodic mean-deviation index must agree; both long holds
a long, both short holds a short, any disagreement closes everything.
Port of FMZ strategy #429488 "Dual Indicator Slight Reversal Trading Strategy" (Combo Backtest 123 Reversal & Ergodic MDI).

FMZ source id: 429488

Source
    https://www.fmz.com/strategy/429488 (PineScript v4, FMZ last modified 2023-10-17 15:45:09).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 178-219), stochastic 14 / 1 / 3, level 50; EMDI 32 / 5 / 5
    123: close[2] < close[1] and close > close[1] and K < D and K > 50 -> 1; mirror -> -1; else pos[1]
    EMDI: u = ema(ema(close - ema(close,32), 5), 5); signal = ema(u, 5); u > signal -> 1; u < signal -> -1; else pos[1]
    both 1 -> entry long; both -1 -> entry short; otherwise strategy.close_all()

Interpretation choices (Pine rules in SURVEY_README.md)
    * SmthLen (3) is an input the function never uses. "Trade reverse" defaults to false and is fixed.
    * A one-bar change from long to short reverses: REVERSAL INTENDED. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and a comparison of two series in the same units.
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

NAME = "fmz_429488_combo_123_ergodic_mdi"
FAMILY = "combo_123_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "r": [32, 16],
    "u": [5, 10],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "r": 32, "s": 5, "u": 5}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    pos1 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())
    e = lambda x, m: x.ewm(span=int(m), adjust=False).mean()  # noqa: E731
    u = e(e(c - e(c, p["r"]), p["s"]), p["u"])
    sig = e(u, p["u"])
    pos2 = _hold((u > sig).to_numpy(), (u < sig).to_numpy())
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
