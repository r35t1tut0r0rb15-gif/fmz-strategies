"""Delayed EMA 20 / 50 state entries, 2-hour bars: the tenth bar after the EMA 20 moves above the EMA 50 goes long (below:
short); the close conditions are written crosswise, so a long is closed on the first bar whose state 11 bars back was
not short, which is normally the bar after the entry (shorts mirrored).
Port of FMZ strategy #430152 "Double Moving Average Crossover Strategy" (Moving Average Cross).

FMZ source id: 430152

Source
    https://www.fmz.com/strategy/430152 (PineScript v4, FMZ last modified 2023-10-25 15:14:35).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 170-200), EMA 20 / 50, delay 10 / 11 bars
    long = ema20 > ema50; short = ema20 < ema50
    longcondition = long and long[10] and not long[11] -> entry long; shortcondition mirrored -> entry short
    closeshort = ema20 > ema50 and not short[11] -> close "Long";  closelong = ema20 < ema50 and not long[11] -> close "Short"

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close conditions are kept exactly as written (their names are crossed in the source):
      "closeshort" closes the long, "closelong" closes the short. As written a long opened on the
      tenth bar of an up state meets "not short[11]" on the next bar and is closed: positions last
      about one bar. Ported as written, stated.
    * Closes act on the position held at the start of the bar and only when the bar's entry does not
      reverse it. The 2015-2019 timestamps are unused.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average states.
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

NAME = "fmz_430152_delayed_ema_state_cross"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "delay": [10, 5],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50, "delay": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    lg, sh = f > s, f < s
    k = int(p["delay"])
    lgk, shk = lg.shift(k, fill_value=False), sh.shift(k, fill_value=False)
    lgk1, shk1 = lg.shift(k + 1, fill_value=False), sh.shift(k + 1, fill_value=False)
    lc = (lg & lgk & ~lgk1).to_numpy()
    sc = (sh & shk & ~shk1).to_numpy()
    close_long = (lg & ~shk1).to_numpy()
    close_short = (sh & ~lgk1).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if lc[i]:
            pos = 1
        elif sc[i]:
            pos = -1
        if start == 1 and pos == 1 and close_long[i]:
            pos = 0
        if start == -1 and pos == -1 and close_short[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
