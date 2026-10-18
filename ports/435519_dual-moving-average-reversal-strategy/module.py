"""Three-bar exhaustion fades, 5-minute bars: three down candles with the last a big down move (body over 70 % of the range) go long
and exit on a close over the previous high; three up candles with a big up move below the SMA 200 go short and exit on a close under
the previous low.
Port of FMZ strategy #435519 "Dual Moving Average Reversal Strategy" (Mean reversion).

FMZ source id: 435519

Source
    https://www.fmz.com/strategy/435519 (PineScript v5, FMZ last modified 2023-12-15 16:38:33).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 152-173), move limit 70 %, SMA 200 (shorts only); the constant 0.001 in the range
    isLongBuy = three down candles and (open - close) / (0.001 + high - low) > 0.7;  isLongExit = close > high[1];  isShortBuy = three up candles and (close - open) / (0.001 + high - low) > 0.7;  isShortExit = close < low[1]
    entry "Entry Long" (isLongBuy), close it (isLongExit);  entry "Entry Short" (close < sma(close, 200) and isShortBuy), close it (isShortExit)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 0.001 added to the range is a price constant (only a division guard; kept as written, it is
      negligible beside any range above a few ticks). A bar that has both an entry and its own
      exit leaves the position flat (the exit is sent after the entry), so an entry signal on such
      a bar is dropped. Opposite entries reverse: REVERSAL INTENDED. FREQ = "5min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle runs and range fractions.
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

NAME = "fmz_435519_three_bar_exhaustion_fade"
FAMILY = "mean_reversion"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "move_limit": [70, 60],
    "ma_length": [200, 100],
}
DEFAULT_PARAMS = {"move_limit": 70, "ma_length": 200}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ma = c.rolling(int(p["ma_length"])).mean()
    down = o > c
    three_down = down & down.shift(1, fill_value=False) & down.shift(2, fill_value=False)
    up = ~down
    three_up = up & up.shift(1, fill_value=True) & up.shift(2, fill_value=True)
    lim = float(p["move_limit"]) / 100.0
    big_dn = ((o - c) / (0.001 + h - lo)) > lim
    big_up = ((c - o) / (0.001 + h - lo)) > lim
    long_buy = (three_down & big_dn).fillna(False)
    long_exit = (c > h.shift(1)).fillna(False)
    short_buy = ((c < ma) & three_up & big_up).fillna(False)
    short_exit = (c < lo.shift(1)).fillna(False)
    return (long_buy & ~long_exit).astype(bool), long_exit.astype(bool), (short_buy & ~short_exit).astype(bool), short_exit.astype(bool)


def portfolio_kwargs(**params):
    return {}
