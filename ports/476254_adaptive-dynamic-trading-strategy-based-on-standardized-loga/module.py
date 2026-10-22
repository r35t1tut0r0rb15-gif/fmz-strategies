"""Z-score of the daily log return over a 50-bar window, broker days: a score under -2 goes long, over +2 goes short; reversing. The 2 % / 4 % bracket is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #476254 "Adaptive Dynamic Trading Strategy Based on Standardized Logarithmic Returns" (Jalambi Paul model).

FMZ source id: 476254

Source
    https://www.fmz.com/strategy/476254 (PineScript v5, FMZ last modified 2024-12-27 14:39:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-139), window 50; threshold 2.0 (constant); stop 2 %, target 4 % of the current close; risk 1 % (unused)
    r = log(close / close[1]);  szi = (r - sma(r, 50)) / stdev(r, 50);  szi < -2 -> entry Buy;  szi > 2 -> entry Sell;  every bar: exit(Buy, stop = close x 0.98, limit = close x 1.04), exit(Sell, mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.stdev is the population deviation over the window. The bracket is re-sent on every bar from
      that bar's close, so its levels move after entry: stops() cannot express a level re-set every bar,
      so it is described here and kept pending (as #438034, mark trailing_stop_pending). The risk
      percentage input is unused. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar bracket described (pending).
    2 generic: PASS, log-return z-score extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored; risk percentage unused.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_476254_log_return_zscore50_extreme_reversal"
FAMILY = "zscore_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "window": [50, 20],
    "threshold": [2.0, 1.5],
}
DEFAULT_PARAMS = {"window": 50, "threshold": 2.0}


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
    r = np.log(c / c.shift(1))
    n = int(p["window"])
    z = (r - r.rolling(n).mean()) / r.rolling(n).std(ddof=0)
    t = float(p["threshold"])
    false = pd.Series(False, index=c.index)
    return z < -t, false, z > t, false.copy()


def portfolio_kwargs(**params):
    return {}
