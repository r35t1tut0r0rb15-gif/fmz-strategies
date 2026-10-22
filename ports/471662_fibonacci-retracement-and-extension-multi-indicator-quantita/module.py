"""Closes against the 10-bar range's retracement levels in the EMA 20 / 50 trend, daily bars: in an up trend a close over any of the 23.6-78.6 % levels (that is, over the 78.6 % level) goes long, in a down trend a close under any of them (under the 23.6 % level) goes short; reversing.
Port of FMZ strategy #471662 "Fibonacci Retracement and Extension Multi Indicator Quantitative Trading Strategy" (Fibonacci Retracement and Extension Strategy).

FMZ source id: 471662

Source
    https://www.fmz.com/strategy/471662 (PineScript v5, FMZ last modified 2024-11-12 10:51:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-151), 10-bar high / low; retracement levels 0.236 / 0.382 / 0.5 / 0.618 / 0.786 from the high (extension levels unused); EMA 20 / 50
    ema20 > ema50: for each level, close > level -> entry Buy;  ema20 < ema50: for each level, close < level -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The loop sends the same entry for every level the close is beyond, so the test is the close
      beyond the lowest (78.6 %) level for longs and the highest (23.6 %) level for shorts. The tests
      are states: repeated entries while held do nothing. There is no exit: positions end at the
      opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, range-level closes in an EMA trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_471662_range10_retracement_side_ema20_50_trend_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "range_len": [10, 20],
    "fast": [20, 10],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"range_len": 10, "fast": 20, "slow": 50}


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
    n = int(p["range_len"])
    hp, lp = h.rolling(n).max(), lo.rolling(n).min()
    lowest_level = hp - (hp - lp) * 0.786
    highest_level = hp - (hp - lp) * 0.236
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (ef > es) & (c > lowest_level)
    se = (ef < es) & (c < highest_level)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
