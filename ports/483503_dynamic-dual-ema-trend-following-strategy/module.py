"""Closes beyond the EMA 44 of highs / lows on the EMA 200 side, broker days: a close over the high EMA above the EMA 200 goes long, a close under the low EMA below it goes short; reversing (the per-bar EMA stops are pending).
Port of FMZ strategy #483503 "Dynamic Dual EMA Trend Following Strategy" (RENTABLE Dual EMA Breakout TSLA).

FMZ source id: 483503

Source
    https://www.fmz.com/strategy/483503 (PineScript v5, FMZ last modified 2025-02-27 16:50:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-140), EMA 44 of high / low; EMA 200 filter on; direction Both; risk 1 % sizing
    close > ema(high, 44) and close > ema200 -> entry Long;  close < ema(low, 44) and close < ema200 -> entry Short
    every bar: exit Long (stop = ema(low, 44));  exit Short (stop = ema(high, 44))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are re-sent on every bar at the moving EMA of lows / highs, so their levels follow the
      price: not ported, mark trailing_stop_pending (as the C185-C189 readings); the opposite entry is the
      exit. The entries are states; a repeat on the side held adds nothing, the other side reverses
      (REVERSAL INTENDED). The direction menu keeps its default (Both); the risk-sized quantity is sizing.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving EMA stops pending.
    2 generic: PASS, EMA-of-extremes breakouts with an EMA 200 filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-sized quantity stored, not ported.
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

NAME = "fmz_483503_ema44_high_low_break_ema200_side_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [44, 20],
    "long_term_length": [200, 100],
}
DEFAULT_PARAMS = {"length": 44, "long_term_length": 200}


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
    n = int(p["length"])
    eh, el = h.ewm(span=n, adjust=False).mean(), lo.ewm(span=n, adjust=False).mean()
    e200 = c.ewm(span=int(p["long_term_length"]), adjust=False).mean()
    le = (c > eh) & (c > e200)
    se = (c < el) & (c < e200)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
