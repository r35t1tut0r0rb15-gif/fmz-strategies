"""Anticipated MACD 12 / 26 / 2 crossings, daily bars, long only: a negative histogram rising above its last two values buys; a positive histogram falling below its last two values sells.
Port of FMZ strategy #473131 "MACD动态波动交叉预测策略-MACD-Dynamic-Oscillation-Cross-Prediction-Strategy" (Demo GPT - Moving Average Convergence Divergence).

FMZ source id: 473131

Source
    https://www.fmz.com/strategy/473131 (PineScript v5, FMZ last modified 2024-11-27 14:54:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-142), MACD 12 / 26, signal EMA 2 (EMA types); date range always on; 100 % of equity, commission 0.1 %, slippage 3
    hist < 0 and hist > hist[1] and hist > hist[2] -> entry Long;  hist > 0 and hist < hist[1] and hist < hist[2] -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * hist_change > 0 repeats hist > hist[1]. The date range flag is fixed true. The entry and exit
      tests cannot hold on the same bar. The equity share and the costs are not ported. Long only. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram turns before the zero cross.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size, commission and slippage stored, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473131_macd_hist_anticipated_cross_long"
FAMILY = "macd_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 21],
    "signal": [2, 9],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    h1, h2 = hist.shift(1), hist.shift(2)
    le = (hist < 0) & (hist > h1) & (hist > h2)
    lx = (hist > 0) & (hist < h1) & (hist < h2)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
