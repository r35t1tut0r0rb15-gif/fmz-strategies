"""SMA 9 / 21 crossings, 1-hour bars: the cross up goes long, the cross down goes short, each with a 1 % stop and 2 % target from the signal close; reversing.
Port of FMZ strategy #472246 "Dual Moving Average Crossover Strategy with Dynamic Risk Management" (BTCUSD Daily Strategy - Market Orders Only).

FMZ source id: 472246

Source
    https://www.fmz.com/strategy/472246 (PineScript v5, FMZ last modified 2024-11-18 15:54:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-150), SMA 9 / 21; stop 1 %, target 2 % of the signal close; initial capital 10000
    crossover(sma9, sma21) and not long -> (close short) entry Market Buy + exit(stop = close x 0.99, limit = close x 1.02)
    crossunder(sma9, sma21) and not short -> (close long) entry Market Sell + exit(stop = close x 1.01, limit = close x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent once on the signal bar from its close: ported as the fixed fractions 0.01 /
      0.02 of the fill. Each close plus the opposite entry is a reversal. The title says daily; the
      backtest header's 1-hour bars are followed. REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the percent bracket as fixed fractions.
    2 generic: PASS, SMA crossings with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only (BTCUSD named in the title)).
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

NAME = "fmz_472246_sma9_21_cross_1_2pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [9, 5],
    "long_len": [21, 50],
    "tp_pct": [0.02, 0.04],
}
DEFAULT_PARAMS = {"short_len": 9, "long_len": 21, "tp_pct": 0.02, "sl_pct": 0.01}


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
