"""MACD 12 / 26 / 9 crosses on the side of an EMA 200 and an SMA 100, 2-hour bars: a MACD cross above its signal line above
zero with the close above both averages goes long; a cross below the signal under zero with the close below both goes
short. Each trade carries a 2 % target and a 1 % stop.
Port of FMZ strategy #434434 "Dual Moving Average Crossover Trend Strategy" (MACD Crossover Trend Strategy Template).

FMZ source id: 434434

Source
    https://www.fmz.com/strategy/434434 (PineScript v4, FMZ last modified 2023-12-06 11:52:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 218-280), MACD 12 / 26 / 9 (EMA), EMA 200, SMA 100; TP 2 % / SL 1 % both sides; date range 2000-2099
    crossover(macd, signal) and macd > 0 and close > ema200 and close > sma100 -> entry long;  crossunder and macd < 0 and below both -> entry short
    exit long (profit = close x 2 % / mintick, loss = close x 1 % / mintick);  exit short the same

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-issued every bar with distances sized from the latest close, so the levels
      move after entry: stops() cannot express that (mark trailing_stop_pending). The port fixes them
      as fractions of the fill: tp_stop 0.02, sl_stop 0.01 (the inputs' defaults in the code).
    * The date window (2000 to 2099) is the author's: dropped. strategy.entry reverses: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark
      coarse_bar_stop. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent exits fixed at entry (approximation stated).
    2 generic: PASS, MACD crosses, average filters and percent exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434434_macd_cross_ema_sma_bracket"
FAMILY = "macd_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [200, 100],
    "tp_pct": [0.02, 0.04],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "ema_len": 200, "sma_len": 100, "tp_pct": 0.02,
                  "sl_pct": 0.01}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    sma = c.rolling(int(p["sma_len"])).mean()
    xu = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    xd = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    le = (xu & (macd > 0) & (c > ema) & (c > sma)).astype(bool)
    se = (xd & (macd < 0) & (c < ema) & (c < sma)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
