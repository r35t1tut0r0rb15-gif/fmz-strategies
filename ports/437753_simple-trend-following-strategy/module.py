"""Channel close breakouts, broker days: a close above the highest high of the previous 20 days goes long, under the lowest low of the previous 20 days goes short; reversing; the 55-day entries can never add.
Port of FMZ strategy #437753 "Simple Trend Following Strategy" (Trend Following).

FMZ source id: 437753

Source
    https://www.fmz.com/strategy/437753 (PineScript v3, FMZ last modified 2024-01-05 13:09:37).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 138-159), fast 20 / slow 55 channels of the previous bars; SMAs 21 / 50 / 100 / 200 plotted only; 10 % of equity
    close > highest(high[1], 20) -> entry Long fast;  close < lowest(low[1], 20) -> entry Short fast;  the same with 55 -> Long slow / Short slow

Interpretation choices (Pine rules in SURVEY_README.md)
    * A 55-day breakout is always also a 20-day breakout on the same bar, and with pyramiding 0 the slow
      ids can never fill once the fast one has: the slow system is unreachable (as #436543 and #437037).
      The channels exclude the current bar ([1]). The SMAs are plotted only; the intraday-loss limit is
      commented out. REVERSAL INTENDED. The 10 % of equity size is sizing. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437753_channel_close_breakout_fast"
FAMILY = "donchian_breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_len": [20, 10],
}
DEFAULT_PARAMS = {"fast_len": 20}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["fast_len"])
    up = c > h.shift(1).rolling(n).max()
    dn = c < lo.shift(1).rolling(n).min()
    false = pd.Series(False, index=bars_df.index)
    return up & ~dn, false, dn & ~up, false.copy()


def portfolio_kwargs(**params):
    return {}
