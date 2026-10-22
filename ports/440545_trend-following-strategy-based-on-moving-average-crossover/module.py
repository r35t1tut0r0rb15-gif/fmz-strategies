"""HMA 25 / HMA 7 crossings, 1-hour bars: the HMA 25 crossing over the HMA 7 goes long, under it short; reversing (as written the slow line is the first argument).
Port of FMZ strategy #440545 "Trend Following Strategy Based on Moving Average Crossover" (MA Crossover Strategy).

FMZ source id: 440545

Source
    https://www.fmz.com/strategy/440545 (PineScript v3, FMZ last modified 2024-01-31 15:17:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 131-178), source close; MA 1 HMA 25, MA 2 HMA 7
    price = security(tickerid, timeframe.period, close);  price1 = hma(price, 25);  price2 = hma(price, 7);  crossover(price1, price2) -> entry Long;  crossunder(price1, price2) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The security call is on the chart's own timeframe, so price is the close. The HMA uses length / 2
      and the rounded square root. As written the long side is the slower average crossing above the
      faster one. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, HMA crossings.
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

NAME = "fmz_440545_hma25_hma7_cross"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [25, 50],
    "ma2": [7, 14],
}
DEFAULT_PARAMS = {"ma1": 25, "ma2": 7}


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
    a, b = _hma(c, int(p["ma1"])), _hma(c, int(p["ma2"]))
    up = (a > b) & (a.shift(1) <= b.shift(1))
    dn = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
