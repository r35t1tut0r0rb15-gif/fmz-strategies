"""MACD side with the EMA 200 side, daily bars: the MACD above its signal with the close above the EMA 200 goes long, the MACD below with the close below goes short; reversing (the "SMC" signals are
inputs fixed true).
Port of FMZ strategy #445468 "MACD与EMA结合的SMC策略SMC-Strategy-Combining-MACD-and-EMA" (SMC with MACD and EMA).

FMZ source id: 445468

Source
    https://www.fmz.com/strategy/445468 (PineScript v5, FMZ last modified 2024-03-19 17:37:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 129-160), MACD 12 / 26 / 9; EMA 200; buy / sell signal inputs true
    buySignal and macd > signal and close > ema200 -> entry Buy;  sellSignal and macd < signal and close < ema200 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Lux Algo SMC signals are two boolean inputs set to true, so they never filter. Both
      conditions are levels: a repeated entry while already on that side is ignored. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD side with an EMA trend side.
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

NAME = "fmz_445468_macd_side_ema200_side_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [200, 100],
    "fast": [12, 8],
}
DEFAULT_PARAMS = {"ema_len": 200, "fast": 12, "slow": 26, "signal": 9}


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
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    le = (macd > sig) & (c > e)
    se = (macd < sig) & (c < e)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
