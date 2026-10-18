"""Close crossing both averages on one bar, broker days: the close crossing over the SMA 9 and the SMA 45 on the same bar goes long; crossing under both goes short (reversing). The "stop at the
previous daily low / high" exit orders are sent on the signal bar of the opposite side, where the reversal already closes the trade.
Port of FMZ strategy #436232 "The moving average crossover strategy is a quantitative trading strategy" (SMA Crossover Strategy (double cross)).

FMZ source id: 436232

Source
    https://www.fmz.com/strategy/436232 (PineScript v5, FMZ last modified 2023-12-22 13:28:01).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 166-195), SMA 9 / 45; stop levels from the previous day's low / high
    buy_condition = crossover(close, sma9) and crossover(close, sma45);  sell_condition = crossunder(close, sma9) and crossunder(close, sma45)
    entry long (buy), entry short (sell);  exit(from_entry = "Long", when = sell_condition, stop = previous day's low);  exit(from_entry = "Short", when = buy_condition, stop = previous day's high)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit orders exist only on the bar of the opposite signal, which also sends the reversing
      entry, so they add nothing (the entry closes the position first); not ported. The previous day's
      levels come from request.security(..., "1D", low[1], lookahead_on) with the [1]: a completed day. Both
      crossings must happen on the same bar (a rare event). REVERSAL INTENDED. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, stop orders sent on the reversing bar: no effect.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG436232 (2 members, best partner #439073, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436232_double_sma_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [45, 30],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 45}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    up = ((c > f) & (c.shift(1) <= f.shift(1))) & ((c > s) & (c.shift(1) <= s.shift(1)))
    dn = ((c < f) & (c.shift(1) >= f.shift(1))) & ((c < s) & (c.shift(1) >= s.shift(1)))
    false = pd.Series(False, index=bars_df.index)
    return up.fillna(False).astype(bool), false, dn.fillna(False).astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
