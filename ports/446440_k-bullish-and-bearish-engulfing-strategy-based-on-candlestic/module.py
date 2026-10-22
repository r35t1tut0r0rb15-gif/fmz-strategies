"""Engulfing candles held for one bar, 2-hour bars: a bullish engulfing bar goes long and a bearish one goes short; every open position is closed at the first bar close it is held, so each trade lasts one bar
unless the opposite pattern reverses it.
Port of FMZ strategy #446440 "基于K线蜡烛图的看涨吞没和看跌吞没策略Bullish-and-Bearish-Engulfing-Strategy-Based-on-Candlestick-Patterns" (Engulfing Strategy).

FMZ source id: 446440

Source
    https://www.fmz.com/strategy/446440 (PineScript v5, FMZ last modified 2024-03-28 16:40:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 117-146), engulfing patterns (open / close only)
    bullishEngulfing -> entry Buy;  bearishEngulfing -> entry Sell;  position_size > 0 -> close Buy (both branches);  position_size < 0 -> close Sell (both branches)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both branches of each exit test close, so a held position is closed at every bar close: it is
      filled at the open after the signal and closed at the next open. The closes are called after the
      entries; a close after a reversing entry on the same bar leaves the reversal. REVERSAL INTENDED. No
      sizing code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, engulfing patterns with a one-bar hold.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446440_engulfing_one_bar_hold_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    o, c = bars_df["open"], bars_df["close"]
    o1, c1 = o.shift(1), c.shift(1)
    bull = ((c1 < o1) & (c > o) & (o <= c1) & (c <= o1)).to_numpy()
    bear = ((c1 > o1) & (c < o) & (o >= c1) & (c >= o1)).to_numpy()
    m = len(bull)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if bull[i] and new != 1:
            le[i], new = True, 1
        if bear[i] and new != -1:
            se[i], le[i], new = True, False, -1
        if pos == 1 and new == 1:
            lx[i], new = True, 0                    # a held long closes at this bar's close
        if pos == -1 and new == -1:
            sx[i], new = True, 0
        pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
