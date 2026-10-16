"""MACD histogram sign with an SMA 200 / EMA 20 filter, long only, 5-minute bars: a positive MACD histogram (above the
SMA 200; below it also the close above the EMA 20) holds a long; a negative histogram (below the SMA 200; above it
also the close below the EMA 20) closes it.
Port of FMZ strategy #429951 "Moving Average Trend Following Golden Cross Long Strategy" (MACD/EMA Long Strategy).

FMZ source id: 429951

Source
    https://www.fmz.com/strategy/429951 (PineScript v2, FMZ last modified 2023-10-23 15:22:48).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 168-205), SMA 200, EMA 20, MACD 12 / 26 / 9
    buy = close > sma200 ? delta > 0 : delta > 0 and close > ema20 -> entry long
    sell = close < sma200 ? delta < 0 : delta < 0 and close < ema20 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * delta = (EMA 12 - EMA 26) - its EMA 9. Long only. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a histogram sign and moving-average sides.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_429951_macd_ema_sma_long"
FAMILY = "macd_momentum"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [200, 100],
    "ema_len": [20, 50],
}
DEFAULT_PARAMS = {"sma_len": 200, "ema_len": 20, "fast": 12, "slow": 26, "signal": 9}


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
    e = lambda x, n: x.ewm(span=int(n), adjust=False).mean()  # noqa: E731
    macd = e(c, p["fast"]) - e(c, p["slow"])
    delta = macd - e(macd, p["signal"])
    sma = c.rolling(int(p["sma_len"])).mean()
    ema = e(c, p["ema_len"])
    buy = ((c > sma) & (delta > 0)) | (~(c > sma) & (delta > 0) & (c > ema))
    sell = ((c < sma) & (delta < 0)) | (~(c < sma) & (delta < 0) & (c < ema))
    false = pd.Series(False, index=bars_df.index)
    return buy.astype(bool), sell.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
