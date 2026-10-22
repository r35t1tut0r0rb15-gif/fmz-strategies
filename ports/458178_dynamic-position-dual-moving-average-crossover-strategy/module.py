"""SMA 9 / 21 crossings with open-price switches, 2-hour bars: the cross up goes long; a long whose bar opened under the SMA 21, or that sees the cross down, switches to short; a short whose bar opened over the SMA 21 switches to long; reversing.
Port of FMZ strategy #458178 "Dynamic Position Dual Moving Average Crossover Strategy" (MA Cross Backtest).

FMZ source id: 458178

Source
    https://www.fmz.com/strategy/458178 (PineScript v5, FMZ last modified 2024-07-30 16:04:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 136-197), SMA 9 / 21; open vs SMA 21 switches; order size 10 (cash)
    crossover(sma9, sma21) -> (short: close Short) entry Long
    long at the close: open < sma21 -> close Long, entry Short;  else crossunder -> close Long, entry Short
    short at the close: open > sma21 -> close Short, entry Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The position tests read the position held into the bar (the orders of a bar fill at the next
      open). The calls are followed in the written order and the later call wins on a bar (#437773): a
      cross-up on a long whose bar opened under the SMA 21 still ends short. Each close-and-enter pair is
      a reversal. The cash order size is not ported (sizing is the optimisation layer's). REVERSAL
      INTENDED. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with open-price switches.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: cash order size stored, not ported.
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

NAME = "fmz_458178_sma9_21_cross_open_vs_sma21_switch_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "shortlen": [9, 5],
    "longlen": [21, 50],
}
DEFAULT_PARAMS = {"shortlen": 9, "longlen": 21}


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
    o, c = bars_df["open"], bars_df["close"]
    a, b = c.rolling(int(p["shortlen"])).mean(), c.rolling(int(p["longlen"])).mean()
    buy = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    sell = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    below = (o < b).to_numpy()
    above = (o > b).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        cur = pos
        if buy[i]:
            cur = 1
        if pos == 1 and (below[i] or sell[i]):
            cur = -1
        if pos == -1 and above[i]:
            cur = 1
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        pos = cur
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
