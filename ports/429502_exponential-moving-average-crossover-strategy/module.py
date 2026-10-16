"""Hourly SMA 3 vs the daily SMA 3, hourly bars: the hourly 3-bar SMA above the 3-day SMA (of completed broker days)
holds a long, below it holds a short.
Port of FMZ strategy #429502 "Exponential Moving Average Crossover Strategy" (Noro's Singapore Strategy).

FMZ source id: 429502

Source
    https://www.fmz.com/strategy/429502 (PineScript v3, FMZ last modified 2023-10-17 16:55:10).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 179-208), big timeframe D, MA length 3
    ma1 = security(tickerid, 'D', sma(close, 3)); ma2 = sma(close, 3)
    ma2 > ma1 -> entry long; ma2 < ma1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * security('D', ...) without lookahead is read as the last completed broker days (17:00
      America/New_York): the SMA 3 of the last three completed daily closes, built inside simulate() from
      the port's own bars. The source's value on the last bar of a day already includes that day (one bar
      earlier): stated approximation.
    * The lot formula is sizing. The date window is dropped.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days.
    2 generic: PASS, a comparison of two averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the lot formula and 100 % of equity stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily values on broker days (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429502_hourly_vs_daily_sma3"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [3, 5],
}
DEFAULT_PARAMS = {"length": 3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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
    n = int(p["length"])
    lab = broker_day(bars_df.index)
    dma = c.groupby(lab).last().rolling(n).mean().shift(1)      # the last completed broker days
    ma1 = pd.Series(dma.reindex(lab).to_numpy(), index=c.index)
    ma2 = c.rolling(n).mean()
    long_e = (ma2 > ma1).astype(bool)
    short_e = (ma2 < ma1).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
