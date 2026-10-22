"""Daily close direction, 1-hour bars: on the first 1-hour bar of each broker day, a completed day that closed above the day before goes long, one that closed below goes short; the position is held
until the opposite day; reversing.
Port of FMZ strategy #440503 "SMART专业量化交易策略SMART-Professional-Quantitative-Trading-Strategy" (Smart Money Concept Strategy).

FMZ source id: 440503

Source
    https://www.fmz.com/strategy/440503 (PineScript v5, FMZ last modified 2024-01-31 10:28:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 161-184), daily close via request.security("D", close) (named OBV, no volume used)
    obv_value = request.security(syminfo.tickerid, "D", close);  obv_slope = obv_value - obv_value[1];  slope > 0 -> entry Long;  slope < 0 -> entry Short;  strategy.close("ExitLong") / ("ExitShort") name no entry

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-5 request.security() without lookahead is read as the last completed higher bar: the
      previous broker day's close on every 1-hour bar, built from the module's own bars. The one-bar
      change of that hourly series is non-zero only on the first bar of a new day, so a signal comes once
      a day. The close calls name ids that are never entered and do nothing. No volume is used despite
      the name. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed days.
    2 generic: PASS, daily close change.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day for the daily close (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440503_daily_close_direction_flip"
FAMILY = "slope_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [1, 3],
}
DEFAULT_PARAMS = {"lookback": 1}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    day = broker_day(bars_df.index)
    dc = c.groupby(day).last()
    k = int(p["lookback"])
    prev_c = pd.Series(dc.shift(1).reindex(day).to_numpy(), index=c.index)      # last completed day
    ref_c = pd.Series(dc.shift(1 + k).reindex(day).to_numpy(), index=c.index)
    first = pd.Series(~pd.Index(day).duplicated(keep="first"), index=c.index)
    slope = (prev_c - ref_c).where(first, 0.0)
    false = pd.Series(False, index=c.index)
    return slope > 0, false, slope < 0, false.copy()


def portfolio_kwargs(**params):
    return {}
