"""Bollinger band breakout, broker days: the close crossing above the upper band (SMA 20 +- 1.2 stdev)
goes long, crossing below the lower band goes short; each position has a 7.5 % stop and, after 5 % of
profit, a trailing stop 0.5 % behind the best price.
Port of FMZ strategy #427592 "Bollinger Band Breakout Trend Following Strategy".

FMZ source id: 427592

Source
    https://www.fmz.com/strategy/427592 (PineScript v4, FMZ last modified 2023-09-22 14:31:17).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 218-275), SMA 20, mult 1.2
    crossover(close, upper) -> entry long; crossunder(close, lower) -> entry short
    exit(loss = close x 7.5 % / mintick, trail_points = close x 5 % / mintick, trail_offset = close x 0.5 % / mintick)

Interpretation choices (Pine rules in SURVEY_README.md; skill section 7)
    * The stop and the trail are ported natively: sl_stop 0.075 and the house trail
      {"type": "percent", "pct": 0.005, "anchor": "high_low", "activate_after": 0.05} (Pine's
      trail follows the best high / low once the profit reaches trail_points). Mark trailing_stop.
      Stated approximation: Pine re-issues the exit every bar with distances scaled by the CURRENT
      close; the house levels scale by the entry / best price (the gap is the move times the small
      percentage, e.g. 0.75 % of a 10 % move for the stop).
    * The year window and the leverage-scaled quantity are dropped / sizing. barstate.isconfirmed is
      true on every historical bar.
    * Daily bars are broker days; stops on daily bars: mark coarse_bar_stop.
    * Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close entries; stop and trail are house stops (approximation stated).
    2 generic: PASS, bands in standard deviations, percent distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity / leverage quantity stored; stops quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import pandas as pd

NAME = "fmz_427592_bb_breakout_pct_trail"
FAMILY = "bollinger_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mult": [1.2, 2.0],
    "trail_pct": [0.5, 2.0],
    "activate": [5.0, 2.5],
}
DEFAULT_PARAMS = {"sma": 20, "mult": 1.2, "loss_pct": 7.5, "trail_pct": 0.5, "activate": 5.0}


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
    n = int(p["sma"])
    basis, dev = c.rolling(n).mean(), p["mult"] * c.rolling(n).std(ddof=0)
    up, lo = basis + dev, basis - dev
    long_e = ((c > up) & (c.shift(1) <= up.shift(1))).astype(bool)
    short_e = ((c < lo) & (c.shift(1) >= lo.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false.copy(), short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["loss_pct"]) / 100,
            "trail": {"type": "percent", "pct": float(p["trail_pct"]) / 100, "anchor": "high_low",
                      "activate_after": float(p["activate"]) / 100}}


def portfolio_kwargs(**params):
    return {}
