"""HPotter combo of the 123 reversal and the Rainbow Oscillator (ten nested SMA 2s), 1-hour bars: long when the 123 state is long and the close is above the rainbow's mean, short on the mirror, flat
otherwise; reversing.
Port of FMZ strategy #442947 "Combo Quantitative Trend Tracking Strategy" (Combo Backtest 123 Reversal & Rainbow Oscillator).

FMZ source id: 442947

Source
    https://www.fmz.com/strategy/442947 (PineScript v4, FMZ last modified 2024-02-27 15:54:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 136-227), 123: stochastic 14, K smoothing 1, D 3, level 50; Rainbow: SMA 2 x 10, HHV / LLV 10; reverse off
    123: close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50 -> 1;  mirrored -> -1;  else previous
    RO: xRBO = 100 (close - mean(ma1..ma10)) / (highest(close, 10) - lowest(close, 10));  xRBO > 0 -> 1, < 0 -> -1, else previous;  both agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both states are levels; disagreement closes. The rainbow width (xRB) only plots. REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close pattern, stochastic and rainbow states.
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

NAME = "fmz_442947_reversal123_rainbow_oscillator_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_ro": [2, 4],
}
DEFAULT_PARAMS = {"length": 14, "length_ro": 2, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "length_hhll": 10, "reverse": False}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def _state(up, dn):
    out = np.zeros(len(up), dtype=np.int8)
    s = 0
    for i in range(len(up)):
        if up[i]:
            s = 1
        elif dn[i]:
            s = -1
        out[i] = s
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    vfast = st.rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    a = _state(((c2 < c1) & (c > c1) & (vfast < vslow) & (vfast > lvl)).to_numpy(),
               ((c2 > c1) & (c < c1) & (vfast > vslow) & (vfast < lvl)).to_numpy())
    lr = int(p["length_ro"])
    mas, x = [], c
    for _ in range(10):
        x = x.rolling(lr).mean()
        mas.append(x)
    mean = sum(mas) / 10
    lb = int(p["length_hhll"])
    rng = (c.rolling(lb).max() - c.rolling(lb).min())
    rbo = (100 * (c - mean) / rng.where(rng != 0)).to_numpy()
    with np.errstate(invalid="ignore"):
        b = _state(rbo > 0, rbo < 0)
    tgt = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0)).astype(np.int8)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
