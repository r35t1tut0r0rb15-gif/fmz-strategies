"""Hull-style WMA crossings, 10-minute bars: 2 x WMA 15 - WMA 30 crossing over its WMA 5 goes long, crossing under goes short; reversing.
Port of FMZ strategy #438975 "Quantitative Trading Strategy Based on Moving Average" (Oracle Move Strategy).

FMZ source id: 438975

Source
    https://www.fmz.com/strategy/438975 (PineScript v3, FMZ last modified 2024-01-16 17:37:13).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 134-162), MA period 30, mode wma
    ma3 = 2 ma(close, 15) - ma(close, 30);  ma4 = ma(ma3, floor(sqrt(30)));  crossover(ma3, ma4) -> entry long;  crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The mode is swept over wma and ema (the alma option is not swept). strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Hull-style average crossings.
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

NAME = "fmz_438975_oracle_hull_style_cross"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [30, 60],
    "mode": ["wma", "ema"],
}
DEFAULT_PARAMS = {"ma_len": 30, "mode": "wma"}


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


def _ma(x, n, mode):
    if mode == "ema":
        return x.ewm(span=n, adjust=False).mean()
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n, mode = int(p["ma_len"]), p["mode"]
    ma3 = 2.0 * _ma(c, n // 2, mode) - _ma(c, n, mode)
    ma4 = _ma(ma3, int(np.floor(np.sqrt(n))), mode)
    up = (ma3 > ma4) & (ma3.shift(1) <= ma4.shift(1))
    dn = (ma3 < ma4) & (ma3.shift(1) >= ma4.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
