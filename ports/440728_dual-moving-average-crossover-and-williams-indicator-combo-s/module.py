"""123 reversal and Accelerator Oscillator combo, 1-hour bars: long when the 123 state is up and the WMA 15 of the AC last turned from negative to positive, short when both are down, flat when they
disagree.
Port of FMZ strategy #440728 "Dual Moving Average Crossover and Williams Indicator Combo Strategy" (Combo Backtest 123 Reversal & Bill Williams AC with Signal Line).

FMZ source id: 440728

Source
    https://www.fmz.com/strategy/440728 (PineScript v3, FMZ last modified 2024-02-01 15:04:51).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 161-213), 123: 14 / 1 / 3 / 50; AC 34 / 5; signal WMA 15 (MA / EMA options off); reverse off
    ao = sma(hl2, 5) - sma(hl2, 34);  ac = ao - sma(ao, 5);  sig = wma(ac, 15);  AC pos = sig[2] < 0 and sig[1] > 0 ? 1 : sig[2] > 0 and sig[1] < 0 ? -1 : previous
    both 1 -> entry Long, both -1 -> entry Short, otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The AC state reads the signal line one and two bars back, as written. The 123 test is read as
      written. The states are levels; disagreement closes. REVERSAL INTENDED. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close pattern, stochastic and the Accelerator Oscillator.
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

NAME = "fmz_440728_reversal123_accelerator_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "n_wma": [15, 9],
}
DEFAULT_PARAMS = {"length": 14, "n_wma": 15, "k_smoothing": 1, "d_length": 3, "level": 50.0, "slow": 34,
                  "fast": 5, "reverse": False}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    vfast = st.rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    up_ = ((c2 < c1) & (c > c1) & (vfast < vslow) & (vfast > lvl)).to_numpy()
    dn_ = ((c2 > c1) & (c < c1) & (vfast > vslow) & (vfast < lvl)).to_numpy()
    hl2 = (h + lo) / 2
    fa = int(p["fast"])
    ao = hl2.rolling(fa).mean() - hl2.rolling(int(p["slow"])).mean()
    ac = ao - ao.rolling(fa).mean()
    sig = _wma(ac, int(p["n_wma"]))
    a_up = ((sig.shift(2) < 0) & (sig.shift(1) > 0)).to_numpy()
    a_dn = ((sig.shift(2) > 0) & (sig.shift(1) < 0)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = pa = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if a_up[i]:
            pa = 1
        elif a_dn[i]:
            pa = -1
        tgt[i] = 1 if (p123 == 1 and pa == 1) else (-1 if (p123 == -1 and pa == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
