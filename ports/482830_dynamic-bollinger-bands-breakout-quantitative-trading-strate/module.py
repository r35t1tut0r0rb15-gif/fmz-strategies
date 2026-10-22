"""Bollinger 20 / 2 (SMA basis) breaks, 2-day bars: a close over the upper band goes long, a close under the lower band closes; long only.
Port of FMZ strategy #482830 "Dynamic Bollinger Bands Breakout Quantitative Trading Strategy" (Demo GPT - Bollinger Bands).

FMZ source id: 482830

Source
    https://www.fmz.com/strategy/482830 (PineScript v6, FMZ last modified 2025-02-20 14:51:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 120-160), Bollinger 20 x 2.0, basis SMA (menu default); 100 % of equity, commission 0.1 %
    close > upper -> entry Long;  close < lower -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The basis menu keeps its default (SMA); the plot offset is drawing only. The entry is a state and
      repeats while the close stays over the band; a repeat adds nothing (default pyramiding). Long only.
      The 100 % of equity size is sizing; the commission is a cost (the house cost model applies). Bars
      are blocks of two broker days (17:00 America/New_York) counted from 1970-01-01, stamped with their
      first minute. FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger band breaks.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482830_bb20_2_upper_break_lower_exit_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper, lower = basis + float(p["mult"]) * sd, basis - float(p["mult"]) * sd
    le = c > upper
    lx = c < lower
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}
