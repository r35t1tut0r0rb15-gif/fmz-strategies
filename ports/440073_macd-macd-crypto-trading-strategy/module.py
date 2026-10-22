"""SMA-MACD histogram sign, 1-hour bars: a MACD of SMA 12 / 26 above its EMA 9 signal holds a long, below it a short; reversing; the entry is sent on every bar of the state.
Port of FMZ strategy #440073 "一个简单高效的MACD量化交易策略MACD-Crypto-Trading-Strategy" (MACD crypto strategy).

FMZ source id: 440073

Source
    https://www.fmz.com/strategy/440073 (PineScript v4, FMZ last modified 2024-01-26 14:20:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 149-191), MACD 12 / 26 with SMA oscillator and EMA 9 signal (fixed in the code)
    macd = sma(close, 12) - sma(close, 26);  signal = ema(macd, 9);  hist > 0 -> entry long;  hist < 0 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A same-side entry while in the position is ignored. strategy.entry reverses: REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram sign.
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

NAME = "fmz_440073_sma_macd_hist_sign_state"
FAMILY = "macd_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_length": [12, 8],
    "slow_length": [26, 50],
}
DEFAULT_PARAMS = {"fast_length": 12, "slow_length": 26, "signal_length": 9}


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
    macd = c.rolling(int(p["fast_length"])).mean() - c.rolling(int(p["slow_length"])).mean()
    hist = macd - macd.ewm(span=int(p["signal_length"]), adjust=False).mean()
    false = pd.Series(False, index=c.index)
    return hist > 0, false, hist < 0, false.copy()


def portfolio_kwargs(**params):
    return {}
