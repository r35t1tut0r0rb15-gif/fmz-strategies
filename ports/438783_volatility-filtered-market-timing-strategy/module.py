"""Buy and hold outside volatility extremes, broker days, long only: while the 10-bar historical volatility is under its 95th percentile of the last 100 bars the long is held; at or above it the long is closed.
Port of FMZ strategy #438783 "Volatility Filtered Market Timing Strategy" (Beat The Market [STRATEGY]).

FMZ source id: 438783

Source
    https://www.fmz.com/strategy/438783 (PineScript v4, FMZ last modified 2024-01-15 12:27:47).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 125-137), upper percentile 95; lookback 100 (only scales the volatility); capital 100000, 100 % of equity
    hv = 100 x stdev(log(close / close[1]), 10) x sqrt(365);  filtered = hv >= percentile_nearest_rank(hv, 100, 95);  not filtered -> entry LONG, else close LONG

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lookback input only multiplies hv, so it cancels in the percentile test; the window is fixed at
      100 bars (current bar included). While the percentile is not yet defined the test is false and the
      long is held, as in Pine. stdev is the population deviation. Long only. The capital and size are
      sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, historical volatility percentile.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital and percent-of-equity size stored.
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

NAME = "fmz_438783_hold_outside_volatility_extremes"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "upper": [95, 90, 80, 99],
}
DEFAULT_PARAMS = {"upper": 95, "window": 100, "hv_len": 10}


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
    hv = 100 * np.log(c / c.shift(1)).rolling(int(p["hv_len"])).std(ddof=0) * np.sqrt(365.0)
    w = int(p["window"])
    rank = int(np.ceil(float(p["upper"]) / 100 * w)) - 1
    pct = hv.rolling(w).apply(lambda a: np.sort(a)[rank], raw=True)
    filt = hv >= pct
    return ~filt, filt, pd.Series(False, index=c.index), pd.Series(False, index=c.index)


def portfolio_kwargs(**params):
    return {}
