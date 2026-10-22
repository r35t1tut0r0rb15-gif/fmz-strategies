"""Engulfing candles with SMA 14 / 60 trend filters, daily bars: a bullish engulfing bar closing above both SMAs goes long, a bearish engulfing bar closing below both goes short; reversing (the morning-star
and dark-cloud branches contradict their own filters and never fire).
Port of FMZ strategy #445804 "Candlestick Pattern Trend Filter Strategy" (Candlestick Pattern Strategy with Trend Filters).

FMZ source id: 445804

Source
    https://www.fmz.com/strategy/445804 (PineScript v5, FMZ last modified 2024-03-22 14:01:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-178), SMA 14 / 60 (titled EMA, a hand-written SMA); 5 % of equity, capital 10000, commission 0.02 %
    long = (bullishEngulfing and close > sma14 and close > sma60 and upTrend) or (morningStar and close < sma60 and upTrend);  short = (bearishEngulfing and below both and downTrend) or (darkCloudCover and close > sma14 and close > sma60 and downTrend)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "ema" lines are the script's own SMA loop. The morning-star branch needs the close under the
      SMA 60 and above it at once, and the dark-cloud branch needs it above and under the SMA 14 at
      once, so neither can fire; both are kept as written. No exit: positions end at the opposite
      entry. strategy.entry reverses: REVERSAL INTENDED. The 5 % of equity size is sizing. FREQ = "1D"
      from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, engulfing patterns with trend filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 5 % of equity size and capital stored.
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

NAME = "fmz_445804_engulfing_sma14_60_trend_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [14, 20],
    "slow": [60, 100],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 60}


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
    o, c = bars_df["open"], bars_df["close"]
    o1, c1, o2, c2 = o.shift(1), c.shift(1), o.shift(2), c.shift(2)
    bull = (c > o) & (o < c1) & (c1 < o1) & (c > o1)
    bear = (c < o) & (o > c1) & (c1 > o1) & (c < o1)
    dark = (c < o) & (o > c1) & (c < o1)
    star = (c2 < o2) & (c1 < o1) & (c1 < c2) & (o1 > c2) & (c > o) & (c > o1)
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    upt = (c > f) & (c > s)
    dnt = (c < f) & (c < s)
    le = (bull & upt) | (star & (c < s) & upt)
    se = (bear & dnt) | (dark & (c > f) & (c > s) & dnt)
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
