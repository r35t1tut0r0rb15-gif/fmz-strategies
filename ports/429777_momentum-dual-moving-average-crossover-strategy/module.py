"""EMA 50 over SMA 50 in a golden-cross regime, long only, hourly bars: EMA 50 above SMA 50 with SMA 50 at or above
SMA 100 holds a long; EMA 50 crossing below SMA 50 closes it.
Port of FMZ strategy #429777 "Momentum Dual Moving Average Crossover Strategy" (Equal-Length EMA/SMA Crossover Strategy).

FMZ source id: 429777

Source
    https://www.fmz.com/strategy/429777 (PineScript v4, FMZ last modified 2023-10-20 16:44:30).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 136-169), momentum 50 (EMA vs SMA), bias SMA 50 / 100
    ema50 > sma50 and sma50 >= sma100 -> entry long; crossunder(ema50, sma50) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The risky / late buy signals are plotted only. Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average comparisons only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 25 % of equity, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429777_ema_sma50_golden_regime_long"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mom_length": [50, 20],
    "bias_slow": [100, 200],
}
DEFAULT_PARAMS = {"mom_length": 50, "bias_fast": 50, "bias_slow": 100}


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
    n = int(p["mom_length"])
    ema, sma = c.ewm(span=n, adjust=False).mean(), c.rolling(n).mean()
    bf, bs = c.rolling(int(p["bias_fast"])).mean(), c.rolling(int(p["bias_slow"])).mean()
    long_e = ((ema > sma) & (bf >= bs)).astype(bool)
    long_x = ((ema < sma) & (ema.shift(1) >= sma.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
