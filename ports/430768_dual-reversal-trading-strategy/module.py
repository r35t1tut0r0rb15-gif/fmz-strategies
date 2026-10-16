"""HPotter combo, 10-minute bars, short only as written: the 123 reversal must agree with the "N bars down" state, which
turns short after the first run of 4 down bars and never resets; both short holds a short, anything else is flat.
Port of FMZ strategy #430768 "Dual Reversal Trading Strategy" (Combo Backtest 123 Reversal & N Bars Down).

FMZ source id: 430768

Source
    https://www.fmz.com/strategy/430768 (PineScript v4, FMZ last modified 2023-11-01 16:49:36).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 223-265), stochastic 14 / 1 / 3, level 50; N bars down 4
    123: close[2] < close[1] and close > close[1] and K < D and K > 50 -> 1; mirror -> -1; else pos[1]
    NBD: counter of consecutive bars with close[1] <= open[1]; counter >= 4 -> posprice := close; pos = posprice > 0 ? -1 : 0
    both 1 -> entry long; both -1 -> entry short; otherwise strategy.close_all()

Interpretation choices (Pine rules in SURVEY_README.md)
    * posprice is set to the close the first time the counter reaches 4 and is never reset, so the
      second state is -1 for the rest of the data: the combination can only be short or flat (it is
      never 1). Ported as written. Short only; Opposite entries cannot occur.
    * "Trade reverse" defaults to false and is fixed. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and bar counts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430768 (2 members, best partner #437694, Jaccard 0.768); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430768_combo_123_n_bars_down"
FAMILY = "combo_123_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "n_length": [4, 6],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "n_length": 4}


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
    down1 = (c.shift(1) <= o.shift(1)).to_numpy()
    up1 = (c.shift(1) > o.shift(1)).to_numpy()
    nl = int(p["n_length"])
    m = len(c)
    pos2 = np.zeros(m, dtype=np.int8)
    cnt, armed = 0, False
    for i in range(m):
        if down1[i]:
            cnt += 1
        elif up1[i]:
            cnt = 0
        if cnt >= nl:
            armed = True
        pos2[i] = -1 if armed else 0
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
