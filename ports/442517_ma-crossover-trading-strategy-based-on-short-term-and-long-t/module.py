"""SMA 34 / 89 crossings with a three-bar time exit, 1-hour bars: the SMA 34 crossing over the SMA 89 goes long, under goes short; two bars after the latest crossing the position is closed (the
fill falls three bars after the signal); reversing.
Port of FMZ strategy #442517 "MA Crossover Trading Strategy Based on Short term and Long term Moving Average Crossovers" (34 89 SMA Crossover Strategy).

FMZ source id: 442517

Source
    https://www.fmz.com/strategy/442517 (PineScript v5, FMZ last modified 2024-02-22 15:36:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 177-228), SMA 34 / 89; exit after 3 candles, exit at open true; morning session 0800-1000 (unused)
    buy = crossover(sma34, sma89);  sell = crossunder;  either -> trade_entry_bar = bar_index;  trade_exit_bar = trade_entry_bar + 3
    exit = bar_index + 1 >= trade_exit_bar (exit at open);  buy -> entry Buy;  sell -> entry Sell;  exit -> close Buy, close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit counts from the latest crossing: it fires at the close of the second bar after it, so
      the position is held for two bars from the fill. The session helper is never called. strategy.entry
      reverses: REVERSAL INTENDED (a crossing resets the count). No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with a bar-count exit.
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

NAME = "fmz_442517_sma34_89_cross_three_bar_exit"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "exit_candles": [3, 6],
    "long_length": [89, 200],
}
DEFAULT_PARAMS = {"exit_candles": 3, "long_length": 89, "short_length": 34, "exit_at_open": True}


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
    c = bars_df["close"]
    s, l_ = c.rolling(int(p["short_length"])).mean(), c.rolling(int(p["long_length"])).mean()
    buy = ((s > l_) & (s.shift(1) <= l_.shift(1))).to_numpy()
    sell = ((s < l_) & (s.shift(1) >= l_.shift(1))).to_numpy()
    k = int(p["exit_candles"])
    early = 1 if p["exit_at_open"] else 0
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held, last = 0, -1
    for i in range(m):
        if buy[i] or sell[i]:
            last = i
        new = held
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if last >= 0 and i + early >= last + k:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
