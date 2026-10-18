"""Close against ten simple averages, broker days: a close over all ten SMAs (10 to 100) goes long; under all ten goes short (reversing).
Port of FMZ strategy #436216 "Multiple Moving Average Comprehensive Strategy" (Multiple Moving Average Strategy).

FMZ source id: 436216

Source
    https://www.fmz.com/strategy/436216 (PineScript v5, FMZ last modified 2023-12-22 11:56:42).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 130-207), SMAs of 10, 20, ..., 100 bars
    buy_signal = close > sma10 and ... and close > sma100;  sell_signal = close < all ten;  buy -> entry Buy, close Sell;  sell -> close Buy, entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The signals are states re-sent every bar. The explicit closes coincide with the reversal. In
      between (close inside the stack) nothing is sent and the position is kept. REVERSAL INTENDED.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average stack.
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

NAME = "fmz_436216_close_vs_ten_smas"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "step": [10, 20],
    "n_ma": [10, 5],
}
DEFAULT_PARAMS = {"step": 10, "n_ma": 10}


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
    mas = [c.rolling(int(p["step"]) * k).mean() for k in range(1, int(p["n_ma"]) + 1)]
    buy = pd.concat([c > m for m in mas], axis=1).all(axis=1)
    sell = pd.concat([c < m for m in mas], axis=1).all(axis=1)
    false = pd.Series(False, index=bars_df.index)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
