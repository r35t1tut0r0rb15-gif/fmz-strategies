"""SMA 5 / 50 cross-ups, daily bars, long only: the cross up buys. The ratcheting stop (the close less 2 standard deviations of ohlc4, raised only) is not ported (pending), so the port has no exit.
Port of FMZ strategy #458043 "Adaptive Moving Average Crossover with Trailing Stop Loss Strategy" (test (SMA 5 / 50 with a ratcheting stdev stop)).

FMZ source id: 458043

Source
    https://www.fmz.com/strategy/458043 (PineScript v5, FMZ last modified 2024-07-29 14:27:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 156-210), SMA 5 / 50; trailing stop close x (1 - 2 x stdev(ohlc4, 20) / close), raised only; quantity (capital + net profit) / close
    crossover(sma5, sma50) -> entry BUY (qty balance / close);  long: stop = max(close - 2 stdev(ohlc4, 20), stop[1]) -> exit(STP, stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is a ratchet on the close less 2 standard deviations of ohlc4, re-sent every bar while
      long; the house trailing types (percent of the best price, k x ATR, lock-in) cannot express it,
      so it is not ported and the module gets the mark trailing_stop_pending (as #440449); without it
      the port has no exit (one long held from the first signal), as #451391. The quantity grows with
      the net profit: sizing. Long only. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the ratcheting stdev stop pending (mark).
    2 generic: PASS, SMA cross-ups.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the balance-based quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458043_sma5_50_cross_up_ratchet_stop_pending_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 10],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 50}


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
    a = c.rolling(int(p["fast"])).mean()
    b = c.rolling(int(p["slow"])).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
