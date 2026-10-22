"""SMA 50 / 200 crossings, 1-hour bars: the cross up goes long, the cross down goes short, each with a 2 % target and 1 % stop from the fill; reversing.
Port of FMZ strategy #458247 "Adaptive Quantitative Trading Strategy with Dual Moving Average Crossover and Take Profit Stop Loss" (Moving Average Crossover Strategy with TP/SL).

FMZ source id: 458247

Source
    https://www.fmz.com/strategy/458247 (PineScript v5, FMZ last modified 2024-07-31 11:41:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 156-211), SMA 50 / 200; target 2 %, stop 1 % of the average price
    crossover(sma50, sma200) -> entry Buy;  crossunder -> close Buy, entry Sell
    long: exit(limit = avg x 1.02, stop = avg x 0.99);  short: exit(limit = avg x 0.98, stop = avg x 1.01)  (every bar while held)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket comes from the average (fill) price and is sent every bar while a trade is open:
      ported active from the fill bar (#440797) as the fixed fractions 0.02 / 0.01 of the fill. The close
      of the long on a cross down comes with the short entry that reverses it (#437773). REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fill-price bracket as fixed fractions.
    2 generic: PASS, SMA crossings with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458247_sma50_200_cross_pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [50, 20],
    "long_len": [200, 100],
    "tp_pct": [0.02, 0.05],
}
DEFAULT_PARAMS = {"short_len": 50, "long_len": 200, "tp_pct": 0.02, "sl_pct": 0.01}


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
    a, b = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["long_len"])).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
