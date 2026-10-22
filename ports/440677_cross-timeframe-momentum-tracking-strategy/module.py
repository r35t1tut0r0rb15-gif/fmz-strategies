"""123 reversal and MACD (8 / 16, SMA signal 11) combo, 1-hour bars: long when the 123 state and the MACD-above-signal state are both up, short when both are down, flat when they disagree.
Port of FMZ strategy #440677 "Cross Timeframe Momentum Tracking Strategy" (Combo Backtest 123 Reversal & MACD Crossover).

FMZ source id: 440677

Source
    https://www.fmz.com/strategy/440677 (PineScript v4, FMZ last modified 2024-02-01 10:21:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-213), 123: 14 / 1 / 3 / 50; MACD 8 / 16 with SMA 11 signal; reverse off
    123 pos (close pattern and stochastic);  MACD pos = sma(macd, 11) < macd ? 1 : > macd ? -1 : previous;  both 1 -> entry Long, both -1 -> entry Short, otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 123 test is read as written. The states are levels; disagreement closes. REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close pattern, stochastic and MACD state.
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

NAME = "fmz_440677_reversal123_macd_state_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "signal_length": [11, 9],
}
DEFAULT_PARAMS = {"length": 14, "signal_length": 11, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "fast_length": 8, "slow_length": 16, "reverse": False}


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
    macd = c.ewm(span=int(p["fast_length"]), adjust=False).mean() - c.ewm(span=int(p["slow_length"]), adjust=False).mean()
    sig = macd.rolling(int(p["signal_length"])).mean()
    m_up, m_dn = (sig < macd).to_numpy(), (sig > macd).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = pm = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if m_up[i]:
            pm = 1
        elif m_dn[i]:
            pm = -1
        tgt[i] = 1 if (p123 == 1 and pm == 1) else (-1 if (p123 == -1 and pm == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
