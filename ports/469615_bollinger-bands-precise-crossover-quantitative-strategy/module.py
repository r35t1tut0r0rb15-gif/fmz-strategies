"""Recoveries from candles entirely outside the Bollinger 20 / 1.2 bands, 1-hour bars: after a candle wholly under the lower band, a close over that candle's high goes long; after a candle wholly over the upper band, a close under its low goes short; reversing.
Port of FMZ strategy #469615 "Bollinger Bands Precise Crossover Quantitative Strategy" (BB BTCUSDT 1HR TF).

FMZ source id: 469615

Source
    https://www.fmz.com/strategy/469615 (PineScript v5, FMZ last modified 2024-10-14 11:38:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 145-187), BB 20, 1.2 sd (population; constants)
    high[1] < lower[1] and low[1] < lower[1] and close > high[1] -> entry Buy;  high[1] > upper[1] and low[1] > upper[1] and close < low[1] -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * There is no exit: positions end at the opposite entry. The title names BTCUSDT; the rules are
      generic. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, outside-band candle recoveries.
    3 crypto-exchange-only: no (exchange pair in the header only (BTCUSDT named in the title)).
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

NAME = "fmz_469615_outside_band_candle_recovery_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "multiplier": [1.2, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "multiplier": 1.2}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["multiplier"]) * c.rolling(n).std(ddof=0)
    lower, upper = basis - dev, basis + dev
    buy_t = (h < lower) & (lo < lower)
    sell_t = (h > upper) & (lo > upper)
    le = buy_t.shift(1, fill_value=False) & (c > h.shift(1))
    se = sell_t.shift(1, fill_value=False) & (c < lo.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
