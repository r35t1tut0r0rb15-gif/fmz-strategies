"""Close crosses of two EMAs, 1-hour bars, long only: the close crossing above the EMA 20 goes long; the close crossing below
the EMA 30 closes the long.
Port of FMZ strategy #431678 "EMA均线交叉策略EMA-Crossover-Strategy" (EMA Cross Strategy with Custom Buy/Sell Conditions).

FMZ source id: 431678

Source
    https://www.fmz.com/strategy/431678 (PineScript v4, FMZ last modified 2023-11-10 15:05:22).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 186-252), fast EMA 1 (the close), EMA 20 buy / EMA 30 sell
    buy = crossunder(ema(close, 20), ema(close, 1)) -> entry "Buy";  sell = crossover(ema(close, 30), ema(close, 1)) -> close "Buy"
    the strategy.close("Sell") lines name an id that is never entered (no effect)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ema(close, 1) is the close. No short is ever entered (the "Sell" closes refer to no entry): long
      only. The close is written after the entry and acts on the position held at the bar's start.
      The date range is always true. Opposite entries cannot occur. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431678_close_ema_20_30_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "buy_len": [20, 50],
    "sell_len": [30, 15],
}
DEFAULT_PARAMS = {"buy_len": 20, "sell_len": 30}


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
    eb = c.ewm(span=int(p["buy_len"]), adjust=False).mean()
    es = c.ewm(span=int(p["sell_len"]), adjust=False).mean()
    buy = ((c > eb) & (c.shift(1) <= eb.shift(1))).to_numpy()
    sell = ((c < es) & (c.shift(1) >= es.shift(1))).to_numpy()
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if buy[i]:
            pos = 1
        if start == 1 and sell[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
