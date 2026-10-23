"""Hourly bars: the MACD 3 / 10 / 16 crossing UNDER its signal on rising volume goes SHORT ("bullish anti-pattern"), crossing over on rising volume goes LONG; each with a 10 % target from the entry price; reversing.
Port of FMZ strategy #441047 "MACD-量能反转交易策略MACD-Volume-Reversal-Trading-Strategy" (MACD Anti-Pattern Detector with Volume (MACD-APD-Vol)).

FMZ source id: 441047

Source
    https://www.fmz.com/strategy/441047 (PineScript v5, FMZ last modified 2024-02-05 10:26:23).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 169-194), MACD 3 / 10 / 16; volume multiplier 1; take profit 10 %
    bullishAntiPattern = crossunder(macd, signal) and volume > volume[1] x 1 -> entry Short;  bearishAntiPattern = crossover(macd, signal) and volume > volume[1] -> entry Long
    exit("Take Profit Long", "Long", limit = avg x 1.10);  exit("Take Profit Short", "Short", limit = avg x 0.90)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "bullish" pattern sells and the "bearish" one buys, as written (weird case). The targets are
      limit orders at the average (fill) price +- 10 %, re-sent every bar with the same level: a fixed
      tp_stop of the fill, exact. There is no stop. REVERSAL INTENDED. No sizing code. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed 10 % target from the fill.
    2 generic: PASS, MACD signal crossings on rising volume, traded contrarian.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the rising-volume test volume > volume[1]; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441047_macd3_10_16_cross_contrarian_volume_10pct_target_1h_reversal"
FAMILY = "macd_variant"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "take_profit": [0.10, 0.03],
    "slow": [10, 26],
}
DEFAULT_PARAMS = {"fast": 3, "slow": 10, "signal": 16, "take_profit": 0.10, "vol_mult": 1.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    vol_up = v > v.shift(1) * float(p["vol_mult"])
    sell = (macd < sig) & (macd.shift(1) >= sig.shift(1)) & vol_up
    buy = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & vol_up
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["take_profit"])}


def portfolio_kwargs(**params):
    return {}
