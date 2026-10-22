"""Close against the HMA 20, 1-hour bars: the close above the Hull MA 20 goes long, below it short; reversing.
Port of FMZ strategy #440362 "EMA Candle Close Strategy" (EMA Candle Close Strategy KHANH 11/11/2023).

FMZ source id: 440362

Source
    https://www.fmz.com/strategy/440362 (PineScript v5, FMZ last modified 2024-01-29 16:02:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 119-146), SMA 1 (the close), HMA 20, EMA 25 (plotted); look-back 55 and channel 40 / 80 plotted only
    longCondition = sma(close, 1) > hma20 and close > hma20 -> entry Long;  else if shortCondition = sma(close, 1) < hma20 or close < hma20 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * sma(close, 1) is the close, so both conditions reduce to the close against the HMA (length / 2
      and the rounded square root); a close equal to it sends nothing. The channels and the EMA only
      feed plots. strategy.entry reverses: REVERSAL INTENDED. The percent-of-equity size, capital and
      commission are sizing and costs. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close against the HMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent of equity, capital and commission settings.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440362_close_vs_hma20"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len2": [20, 50],
}
DEFAULT_PARAMS = {"len2": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(src, n):
    return _wma(2 * _wma(src, n // 2) - _wma(src, n), int(round(np.sqrt(n))))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    h = _hma(c, int(p["len2"]))
    false = pd.Series(False, index=c.index)
    return c > h, false, c < h, false.copy()


def portfolio_kwargs(**params):
    return {}
