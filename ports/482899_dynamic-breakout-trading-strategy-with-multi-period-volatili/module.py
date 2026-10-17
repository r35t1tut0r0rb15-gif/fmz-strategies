"""Closes beyond the previous 10-bar high (low) by 0.05 %, with a 0.2 % trailing stop that starts after 0.5 % of
profit, two-day bars: a close above the prior 10-bar high x 1.0005 goes long; below the prior 10-bar low x 0.9995
goes short.
Port of FMZ strategy #482899 "动态突破追踪止损交易策略基于波动率的多周期价格突破模型-Dynamic-Breakout-Trading-Strategy-with-Multi-Period-Volatility-Based-Price-Breakthrough-Model" (Breakout Strategy with Trailing Stop).

FMZ source id: 482899

Source
    https://www.fmz.com/strategy/482899 (PineScript v5, FMZ last modified 2025-02-27 17:27:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 99-130), lookback 10, threshold 0.05 %, stop 0.2 %, trail start 0.5 %,
pyramiding 100
    breakoutHigh = close > highest(high[1], 10) x 1.0005 and more than 1 hour since the last entry -> entry long
    breakoutLow mirrored -> entry short
    while held: exit(trail_points = close x 0.5 %, trail_offset = close x 0.2 %)

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding = 100 adds on every breakout bar: adds are sizing, not ported (net position only, as #490570).
    * The trail arguments are ticks given price distances: read as price distances (as #427592); in percent of the
      current close they become the house trail {"type": "percent", "pct": 0.002, "anchor": "high_low",
      "activate_after": 0.005}. Mark trailing_stop.
    * The 1-hour spacing between entries always holds on two-day bars (as written).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Two-day bars are blocks of broker-day
      dates from 1970-01-01 (decision owed, as #426509); FREQ = "2D" from the backtest header; coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close entries; the trail a house trail.
    2 generic: PASS, rolling extremes and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the pyramiding adds quoted in original_sizing.txt, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in two-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482899_breakout_pct_trail_2d"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [0.2, 1.0],
    "lookback": [10, 20],
}
DEFAULT_PARAMS = {"lookback": 10, "threshold_pct": 0.05, "trail_pct": 0.2, "activate_pct": 0.5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=2):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["lookback"])
    k = p["threshold_pct"] / 100
    long_e = (c > h.shift(1).rolling(n).max() * (1 + k)).astype(bool)
    short_e = ((c < lo.shift(1).rolling(n).min() * (1 - k)) & ~long_e).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]) / 100, "anchor": "high_low",
                      "activate_after": float(p["activate_pct"]) / 100}}


def portfolio_kwargs(**params):
    return {}
