"""Open-close cross of DEMA 14 lines taken from the day's last 2-hour bar, broker days: the DEMA of closes crossing over the DEMA of opens goes long, crossing under goes short; reversing; each trade has a
small trailing stop in tick distances, re-expressed as an ATR multiple after a minimum gain.
Port of FMZ strategy #438800 "Open Close Cross Moving Average Trend Following Strategy" (OCC Strategy).

FMZ source id: 438800

Source
    https://www.fmz.com/strategy/438800 (PineScript v4, FMZ last modified 2024-01-15 14:24:27).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 198-275), alternate resolution on, "120" (on a 1-day chart); MA on, DEMA 14; trailing stop on, trail points 200, offset 400 (ticks)
    closeSeries = security(tickerid, "120", dema(close, 14));  openSeries = security(tickerid, "120", dema(open, 14));  crossover -> entry long;  crossunder -> entry short
    exit(trail_points = 200, trail_offset = 400) for each side;  exit(when = opposite cross) with no levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 2-hour values requested from a daily chart are the day's LAST 2-hour bar (as #436765), counted
      from the broker day's start (17:00 America/New_York); the DEMAs run on that 2-hour series.
    * Criterion 2: the trail activates after 200 ticks of gain and trails 400 ticks behind the best
      price; as the house volatility trail: k = 0.04 x ATR(14) of the daily bars behind the best high
      (low), active after a gain of 0.0007 of the fill (the reading: 20 and 40 on BTC with 0.1 ticks
      against a daily ATR near 1000 and a price near 29000), and a wider pair 1.0 / 0.01 (anchor high_low;
      mark trailing_stop). The level-free exits place nothing. strategy.entry reverses: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop.
      No sizing code. Daily bars are broker days, stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; house trail.
    2 generic: ADAPT, tick trail -> ATR multiple and fraction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the trail inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_438800_occ_dema_2h_cross_trail"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_trail": [0.04, 1.0],
    "activate": [0.0007, 0.01],
}
DEFAULT_PARAMS = {"k_trail": 0.04, "activate": 0.0007, "basis_len": 14, "res_minutes": 120, "atr_len": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _dema(x, n):
    e = x.ewm(span=n, adjust=False).mean()
    return 2 * e - e.ewm(span=n, adjust=False).mean()


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    # 2-hour bars counted from each broker day's start (17:00 America/New_York)
    ny = df.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)
    mos = (ny - ny.normalize()) // pd.Timedelta(minutes=int(p["res_minutes"]))
    b2 = df.groupby([lab, np.asarray(mos)]).agg({"open": "first", "close": "last"})
    n = int(p["basis_len"])
    last2 = pd.DataFrame({"occ_close": _dema(b2["close"], n), "occ_open": _dema(b2["open"], n)})
    day = last2.index.get_level_values(0)
    last2 = last2[~day.duplicated(keep="last")]        # the day's last 2-hour bar
    last2.index = last2.index.get_level_values(0)
    bars = bars.join(last2)
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    cs, os_ = bars_df["occ_close"], bars_df["occ_open"]
    up = (cs > os_) & (cs.shift(1) <= os_.shift(1))
    dn = (cs < os_) & (cs.shift(1) >= os_.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["k_trail"]),
                      "anchor": "high_low", "activate_after": float(p["activate"])}}


def portfolio_kwargs(**params):
    return {}
