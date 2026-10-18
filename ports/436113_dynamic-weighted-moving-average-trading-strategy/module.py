"""SMA 5 / 10 crossings in an EMA 30 trend, broker days: the SMA 5 crossing over the SMA 10 with the close over the EMA 30 goes long; crossing under with the close under the EMA goes short
(reversing).
Port of FMZ strategy #436113 "Dynamic Weighted Moving Average Trading Strategy" (Estrategia Mejorada para Criptomonedas).

FMZ source id: 436113

Source
    https://www.fmz.com/strategy/436113 (PineScript v5, FMZ last modified 2023-12-21 12:19:43).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 112-128), SMA 5 / 10; EMA 30
    longCondition = crossover(sma5, sma10) and close > ema30;  shortCondition = crossunder(sma5, sma10) and close < ema30;  entry long / short

Interpretation choices (Pine rules in SURVEY_README.md)
    * REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average cross and a trend filter.
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

NAME = "fmz_436113_sma_cross_ema_filter"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 3],
    "ema_len": [30, 50],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 10, "ema_len": 30}


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
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    le = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > ema)).fillna(False).astype(bool)
    se = ((f < s) & (f.shift(1) >= s.shift(1)) & (c < ema)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
