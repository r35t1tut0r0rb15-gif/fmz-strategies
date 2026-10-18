"""MACD crossing bought below the Bollinger mid line, 1-hour bars, long only: a MACD crossing over its signal with the RSI under 50 and the close under the 20-bar average goes long; an RSI over 70 with the close over
the upper band closes the long. The optional stop (off by default) is not ported.
Port of FMZ strategy #436593 "A Multi Period Trading Strategy Based on Moving Averages" (MACD + BB + RSI [Alorse]).

FMZ source id: 436593

Source
    https://www.fmz.com/strategy/436593 (PineScript v4, FMZ last modified 2023-12-26 10:13:34).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 181-246), MACD 12 / 26 / 9 (EMA), Bollinger 20 / 2, RSI 14; stop off
    buy = crossover(macd, signal) and rsi < 50 and close < basis;  sell = rsi > 70 and close > upper;  entry Long when buy;  close Long when sell;  exit "Stop Loss" (percent or ATR) only when useSL

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop loss switch is off by default and its levels (a fraction of the average price, or a
      valuewhen ATR level) are not ported. Bollinger deviation is the population form. Long only. The
      20 % of equity size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: REVIEW, optional stop off by default.
    2 generic: PASS, MACD crossing with band and RSI filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and the stop inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436593_macd_bb_rsi_dip"
FAMILY = "macd_signal"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_length": [12, 8],
    "length": [20, 30],
}
DEFAULT_PARAMS = {"fast_length": 12, "slow_length": 26, "signal_length": 9, "length": 20, "mult": 2.0,
                  "rsi_len": 14, "rsi_buy": 50, "rsi_sell": 70}


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
    macd = c.ewm(span=int(p["fast_length"]), adjust=False).mean() - c.ewm(span=int(p["slow_length"]), adjust=False).mean()
    signal = macd.ewm(span=int(p["signal_length"]), adjust=False).mean()
    n = int(p["length"])
    basis = c.rolling(n).mean()
    upper = basis + float(p["mult"]) * c.rolling(n).std(ddof=0)
    r = int(p["rsi_len"])
    ch = c.diff()
    up_ = ch.clip(lower=0).ewm(alpha=1 / r, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / r, adjust=False).mean()
    rsi = (100 - 100 / (1 + up_ / dn_)).where(dn_ != 0, 100.0).where(up_.notna())
    buy = ((macd > signal) & (macd.shift(1) <= signal.shift(1)) & (rsi < float(p["rsi_buy"])) & (c < basis))
    sell = (rsi > float(p["rsi_sell"])) & (c > upper)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.fillna(False).astype(bool), sell.fillna(False).astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
