"""MACD histogram turns, broker days, long only: a rising histogram two bars in a row (this bar over the last, the last over the one
before) goes long; the histogram falling under its value two bars back closes the long.
Port of FMZ strategy #435495 "MACD长线反转策略MACD-Long-Reversal-Strategy" (MACD Long Strat).

FMZ source id: 435495

Source
    https://www.fmz.com/strategy/435495 (PineScript v4, FMZ last modified 2023-12-15 13:55:38).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 118-141), MACD 6 / 26 with an SMA 9 signal
    histogram = macd - sma(macd, 9);  LongEntryCondition = histogram > histogram[1] and histogram[1] > histogram[2];  exitConditionLong = histogram < histogram[2]
    LongEntryCondition -> entry long;  exitConditionLong -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The names say "reversing negative" but the test is two rising bars, as written. Long only.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, momentum histogram turns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435495_macd_histogram_turn_long"
FAMILY = "macd_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [6, 12],
    "slow": [26, 21],
}
DEFAULT_PARAMS = {"fast": 6, "slow": 26, "signal": 9}


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
    hist = macd - macd.rolling(int(p["signal"])).mean()
    le = ((hist > hist.shift(1)) & (hist.shift(1) > hist.shift(2))).fillna(False).astype(bool)
    lx = (hist < hist.shift(2)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
