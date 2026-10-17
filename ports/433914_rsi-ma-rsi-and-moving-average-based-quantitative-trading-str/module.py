"""RSI against its SMA, contrarian, 1-hour bars: the RSI 14 crossing below its SMA 9 goes long, crossing above it goes
short; always in after the first cross.
Port of FMZ strategy #433914 "基于RSI和MA均线的量化交易策略RSI-and-Moving-Average-Based-Quantitative-Trading-Strategy" (RSI + MA).

FMZ source id: 433914

Source
    https://www.fmz.com/strategy/433914 (PineScript v4, FMZ last modified 2023-12-01 14:21:18).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 186-211), RSI 14, MA 9, reverse trade false
    buy = rsi[1] > ma[1] and rsi < ma -> entry long;  sell = rsi[1] < ma[1] and rsi > ma -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * With "reverse trade" off the long follows the RSI falling under its average, as written.
      strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an oscillator against its own average.
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

NAME = "fmz_433914_rsi_ma_contrarian_cross"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "ma_len": [9, 21],
}
DEFAULT_PARAMS = {"rsi_len": 14, "ma_len": 9}


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
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    ma = r.rolling(int(p["ma_len"])).mean()
    le = ((r.shift(1) > ma.shift(1)) & (r < ma)).astype(bool)
    se = ((r.shift(1) < ma.shift(1)) & (r > ma)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
