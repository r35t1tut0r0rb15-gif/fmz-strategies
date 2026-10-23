"""Broker days: the EMA 9 crossing over the EMA 21 goes long, crossing under goes short; reversing.
Port of FMZ strategy #454766 "Multi Indicator Composite Trend Following Strategy" (Comb Backtest Debug).

FMZ source id: 454766

Source
    https://www.fmz.com/strategy/454766 (PineScript v5, FMZ last modified 2024-06-21 18:12:28).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 180-282), EMA 9 / 21 ("simplified for testing"); supertrend 10 x 3, RSI 14, BB 20 x 2, VWAP plotted only
    buyCondition = crossover(ema9, ema21) -> entry Buy;  sellCondition = crossunder(ema9, ema21) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the EMA crossings place orders ("Simplified Buy and Sell Conditions for Testing"); the
      supertrend, RSI, Bollinger bands and VWAP only plot or alert: volume is not used (held for volume,
      not used). REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA 9 / 21 crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454766_ema9_21_cross_debug_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return up.astype(bool), false, dn.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
