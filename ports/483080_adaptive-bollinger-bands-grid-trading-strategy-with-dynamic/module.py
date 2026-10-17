"""Bollinger-band grid crosses, always in the market, daily (broker-day) bars: the close crossing above any of four
levels 1-4 % above the lower band goes long; crossing below any of four levels 1-4 % under the upper band goes short.
Port of FMZ strategy #483080 "自适应布林网格交易策略-Adaptive-Bollinger-Bands-Grid-Trading-Strategy-with-Dynamic-Level-Adjustment" (Grid Bot based on Bollinger Bands with Adjustable Levels).

FMZ source id: 483080

Source
    https://www.fmz.com/strategy/483080 (PineScript v6, FMZ last modified 2025-02-27 17:04:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 105-148), BB 20 x 2, grid distance 1 %, 4 levels
    longLevel_i = lower x (1 + 1 % x (i + 1)); shortLevel_i = upper x (1 - 1 % x (i + 1)), i = 0..3
    crossover(close, longLevel_0) -> entry "GridLong"; in a for loop i = 1..3: crossover(close, longLevel_i) ->
    entry "GridLong<i>" (shorts mirrored with crossunder)

Interpretation choices (Pine rules in SURVEY_README.md)
    * One position (pyramiding default 1): the grid ids add nothing while held; a long entry reverses a short
      (REVERSAL INTENDED). No exits, no stops.
    * The crosses inside the for loop share one call site: their previous-bar values are those written on the
      previous bar's LAST iteration, so for i = 1..3 the test is close > level_i and close[1] <= level_3[1] (shorts:
      close < level_i and close[1] >= level_3[1]), as written. The level-0 crosses are ordinary. A long and a short
      entry on one bar: the later (short) wins, as in Pine.
    * ta.stdev is the population standard deviation. Daily bars are broker days (17:00 America/New_York) stamped with
      their first minute (as #430984). FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands and percentage offsets.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults); the grid ids are not adds (one position).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483080_bollinger_grid_level_crosses_1d"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "grid_pct": [1.0, 2.0],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "grid_pct": 1.0, "grid_size": 4}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = p["mult"] * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    g, k = p["grid_pct"] / 100, int(p["grid_size"])
    longs = [lower * (1 + g * (i + 1)) for i in range(k)]
    shorts = [upper * (1 - g * (i + 1)) for i in range(k)]
    c1 = c.shift(1)
    long_e = (c > longs[0]) & (c1 <= longs[0].shift(1))
    short_e = (c < shorts[0]) & (c1 >= shorts[0].shift(1))
    last_l, last_s = longs[-1].shift(1), shorts[-1].shift(1)   # the loop call site's previous value
    for i in range(1, k):
        long_e |= (c > longs[i]) & (c1 <= last_l)
        short_e |= (c < shorts[i]) & (c1 >= last_s)
    short_e = short_e.astype(bool)
    long_e = (long_e & ~short_e).astype(bool)   # both on one bar: the later short entry wins
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
