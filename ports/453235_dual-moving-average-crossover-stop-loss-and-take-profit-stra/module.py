"""EMA 5 / 200 crossings, 1-hour bars: the cross up goes long and the cross down goes short, each with a stop 50 and a target 200 price units from the fill (0.00119 / 0.00476 at BTC 42000); reversing.
Port of FMZ strategy #453235 "Dual Moving Average Crossover Stop Loss and Take Profit Strategy" (EMA5 Cross EAM200 && SL/TP 50 and 200 Point Target).

FMZ source id: 453235

Source
    https://www.fmz.com/strategy/453235 (PineScript v5, FMZ last modified 2024-06-03 11:02:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-158), EMA 5 / 200 (EMA 13 / 20 plotted only); stop 50 / target 200 points from the average price
    crossover(ema5, ema200) -> entry Long;  crossunder -> entry Short;  long: exit(stop = avg - 50, limit = avg + 200);  short: exit(stop = avg + 50, limit = avg - 200)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 'points' are price amounts added to the average price: read against BTC near 42000 like
      other price units (#440456), they are ported as the fixed fractions 50 / 42000 and 200 / 42000
      of the fill, active from the fill bar (#440797). The bar counter is unused. REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the price-unit bracket as fractions of 42000.
    2 generic: PASS, EMA 5 / 200 crossings.
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

NAME = "fmz_453235_ema5_200_cross_point_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_frac": [0.00119, 0.01],
    "tp_frac": [0.00476, 0.02],
}
DEFAULT_PARAMS = {"sl_frac": 0.00119, "tp_frac": 0.00476, "fast": 5, "slow": 200}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
