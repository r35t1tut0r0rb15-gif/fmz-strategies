"""MACD 12 / 26 / 9 crossings, 1-hour bars: the cross up goes long and the cross down goes short, each with a 50-point stop and a 100-point target from the fill (0.00119 / 0.00238 at BTC 42000); reversing.
Port of FMZ strategy #458027 "MACD交叉动量策略与动态止盈止损优化-MACD-Crossover-Momentum-Strategy-with-Dynamic-Take-Profit-and-Stop-Loss-Optimization" (MACD Strategy (point bracket)).

FMZ source id: 458027

Source
    https://www.fmz.com/strategy/458027 (PineScript v5, FMZ last modified 2024-07-29 13:35:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-210), MACD 12 / 26 / 9; target 100 / stop 50 points from the average price
    crossover(macd, signal) -> entry Long;  crossunder -> entry Short;  exit(Long, limit = avg + 100, stop = avg - 50);  exit(Short, limit = avg - 100, stop = avg + 50)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The points are price amounts added to the average price: read against BTC near 42000 like other
      price units (#440456), they are ported as the fixed fractions 50 / 42000 and 100 / 42000 of the
      fill, active from the fill bar (#440797). REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the price-unit bracket as fractions of 42000.
    2 generic: PASS, MACD crossings.
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

NAME = "fmz_458027_macd_cross_point_bracket_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_frac": [0.00119, 0.01],
    "tp_frac": [0.00238, 0.02],
}
DEFAULT_PARAMS = {"sl_frac": 0.00119, "tp_frac": 0.00238}


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
    c = bars_df["close"]
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    se = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
