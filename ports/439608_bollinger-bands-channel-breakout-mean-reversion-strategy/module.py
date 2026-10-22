"""Lower Bollinger band reclaims, long only, broker days: the close crossing back over the lower band (20, 2) goes long with a stop at the signal bar's low; the upper-band target re-sent every bar is not ported.
Port of FMZ strategy #439608 "Bollinger Bands Channel Breakout Mean Reversion Strategy" (bb 2ND target).

FMZ source id: 439608

Source
    https://www.fmz.com/strategy/439608 (PineScript v5, FMZ last modified 2024-01-22 10:47:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-182), Bollinger 20 x 2 of close; date filter true; EMA 20 (plot only)
    crossover(close, lower) -> stopLossPrice := low, entry Long (qty 1);  exit(ProfitTarget2, from Long, limit = upper) every bar;  exit(StopLoss, stop = stopLossPrice) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the low of the signal bar: sl_stop = (close - low) / close of the signal bar, shifted
      one bar inside stops() and re-based on the fill (a low equal to the close places no stop); a new
      signal while long moves the script's stop, which the port does not follow. The target is re-sent
      every bar at the current upper band, a moving level the house stops cannot express: not ported,
      mark trailing_stop_pending. Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on
      1-day bars: mark coarse_bar_stop. The size of 1 is sizing. Daily bars are broker days, stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving target pending.
    2 generic: PASS, Bollinger crossings and the signal-bar low.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_439608_lower_band_reclaim_low_stop_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


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


def _signal(bars_df, p):
    c = bars_df["close"]
    n = int(p["length"])
    lower = c.rolling(n).mean() - float(p["mult"]) * c.rolling(n).std(ddof=0)
    return (c > lower) & (c.shift(1) <= lower.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le = _signal(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sl = ((c - bars_df["low"]) / c).where(_signal(bars_df, p))
    return {"sl_stop": sl.where(sl > 0).shift(1)}


def portfolio_kwargs(**params):
    return {}
