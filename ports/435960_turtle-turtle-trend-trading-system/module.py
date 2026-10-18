"""Turtle channel breakouts, 1-hour bars: a close over the previous 55-bar high goes long, under the previous 55-bar low goes short (reversing);
a long is closed when the low breaks the previous 20-bar low, a short when the high breaks the previous 20-bar high.
Port of FMZ strategy #435960 "趋势追踪-turtle系统Turtle-Trend-Trading-System" (Turtle System).

FMZ source id: 435960

Source
    https://www.fmz.com/strategy/435960 (PineScript v4, FMZ last modified 2023-12-20 14:16:48).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 150-168), entry length 55, exit length 20
    close > highest(55)[1] -> entry long;  close < lowest(55)[1] -> entry short;  low < lowest(20)[1] -> close long;  high > highest(20)[1] -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest(n) / lowest(n) with one argument read the highs / lows; the channel is the previous bar's
      (the bar is not in its own window). The four orders of one bar are filled in the script's call
      order at the next open (entry long, entry short, close long, close short): a bar that both
      enters and meets its own exit ends flat. REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel breakouts.
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

NAME = "fmz_435960_turtle_55_20_channel"
FAMILY = "breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [55, 40],
    "e": [20, 10],
}
DEFAULT_PARAMS = {"n": 55, "e": 20}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, e = int(p["n"]), int(p["e"])
    hi_n, lo_n = h.rolling(n).max().shift(1), lo.rolling(n).min().shift(1)
    hi_e, lo_e = h.rolling(e).max().shift(1), lo.rolling(e).min().shift(1)
    e_l = (c > hi_n).fillna(False).to_numpy()
    e_s = (c < lo_n).fillna(False).to_numpy()
    c_l = (lo < lo_e).fillna(False).to_numpy()
    c_s = (h > hi_e).fillna(False).to_numpy()
    m = len(e_l)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    pend = None
    for i in range(m):
        if i > 0 and pend is not None:          # fills at this bar's open, in the script's call order
            a, b, cc, d = pend
            if a and pos <= 0:
                pos = 1
            if b and pos >= 0:
                pos = -1
            if cc and pos == 1:
                pos = 0
            if d and pos == -1:
                pos = 0
        held[i] = pos
        pend = (bool(e_l[i]), bool(e_s[i]), bool(c_l[i]), bool(c_s[i]))
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
