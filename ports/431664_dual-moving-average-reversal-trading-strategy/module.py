"""Two-candle colour fades (yeainshukla), 1-hour bars: two red candles in a row go long, two green candles in a row go
short; a position older than 280 hours is closed.
Port of FMZ strategy #431664 "Dual Moving Average Reversal Trading Strategy" (BuyRedSellGreen4H).

FMZ source id: 431664

Source
    https://www.fmz.com/strategy/431664 (PineScript v5, FMZ last modified 2023-11-10 11:18:38).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 129-179), two-candle colour rule, time exit 1008000000 ms
    close < open and close[1] < open[1] -> entry long (close short);  else close[1] > open[1] -> entry short (close long)
    position open and time - entry time > 1008000000 ms (280 h) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "else" branch takes every bar that is not red (close >= open) with a green previous bar, as
      written. The exits named with no levels place nothing. The 2023-09-18 to 2023-12-31 window is
      the author's: dropped. The time exit counts from the entry fill (the open after the signal) and
      is a close-checked exit (not a time stop); it does not undo a reversal on the same bar.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header (the title's
      4h is not the header's).

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked time exit.
    2 generic: PASS, candle colours and a holding time.
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

NAME = "fmz_431664_two_candle_colour_fade"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "max_hours": [280, 72],
    "bars": [2, 3],
}
DEFAULT_PARAMS = {"max_hours": 280, "bars": 2}


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
    o, c = bars_df["open"], bars_df["close"]
    red, green = (c < o).to_numpy(), (c > o).to_numpy()
    k = int(p["bars"])
    m = len(red)
    lg, sh = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    for i in range(k - 1, m):
        prev_red = all(red[i - j] for j in range(1, k))
        prev_green = all(green[i - j] for j in range(1, k))
        if red[i]:
            lg[i] = prev_red
        else:
            sh[i] = prev_green
    t = bars_df.index.asi8 // 1_000_000                   # bar open time, ms
    lim = float(p["max_hours"]) * 3_600_000
    tgt = np.zeros(m, dtype=np.int8)
    pos, fill_t = 0, None
    for i in range(m):
        start = pos
        if lg[i]:
            pos = 1
        elif sh[i]:
            pos = -1
        if start != 0 and fill_t is not None and t[i] - fill_t > lim and pos == start:
            pos = 0
        if pos != start and pos != 0:
            fill_t = t[i + 1] if i + 1 < m else None
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
