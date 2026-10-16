"""Three-SMA alignment with a confirmation delay, as written: the SMA 20 > 50 > 200 alignment that
began exactly 5 bars ago and still holds goes long; the mirror goes short. As the script names its
closes, a long is closed while the long alignment holds without a short alignment 6 bars back (so a
long lasts about one bar), and a short likewise.
Port of FMZ strategy #427445 "Simple Moving Average Crossover Strategy".

FMZ source id: 427445

Source
    https://www.fmz.com/strategy/427445 (PineScript v4, FMZ last modified 2023-09-21 10:47:24).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 142-170), SMA 20 / 50 / 200, wait 5 / 5
    long = top > mid > low; short = top < mid < low
    long_condition = long and long[5] and not long[6]; short_condition mirrors
    close_long = short and not long[6]; close_short = long and not short[6]
    entry long on long_condition; entry short on short_condition
    strategy.close("LongPosition", when = close_short); strategy.close("ShortPosition", when = close_long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Ported AS WRITTEN: the long is closed by `close_short` (a LONG alignment), the short by
      `close_long`. A close only acts on a position already open when the bar's orders are placed
      (Pine), so a long opened at bar t+1 is closed after bar t+1 if the alignment holds: longs last
      about one bar. The evidently intended version (swapped close conditions) is a decision owed.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427445_three_sma_delay_as_written"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bars_wait": [5, 2, 10],
    "sma_low": [200, 100],
}
DEFAULT_PARAMS = {"sma_top": 20, "sma_mid": 50, "sma_low": 200, "bars_wait": 5}


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
    t, mid, low = (c.rolling(int(p[k])).mean() for k in ("sma_top", "sma_mid", "sma_low"))
    lng = (t > mid) & (mid > low)
    sht = (t < mid) & (mid < low)
    k = int(p["bars_wait"])
    l_k, l_k1 = lng.shift(k, fill_value=False), lng.shift(k + 1, fill_value=False)
    s_k, s_k1 = sht.shift(k, fill_value=False), sht.shift(k + 1, fill_value=False)
    long_c = (lng & l_k & ~l_k1).to_numpy()
    short_c = (sht & s_k & ~s_k1).to_numpy()
    close_long_pos = (lng & ~s_k1).to_numpy()     # the source's `close_short`, used on the long
    close_short_pos = (sht & ~l_k1).to_numpy()    # the source's `close_long`, used on the short
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        elif pos == 1 and close_long_pos[i]:
            pos = 0
        elif pos == -1 and close_short_pos[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
