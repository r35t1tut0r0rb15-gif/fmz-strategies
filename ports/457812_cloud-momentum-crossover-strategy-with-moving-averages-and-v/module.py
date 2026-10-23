"""Broker days: the close above "span A" (the average of SMA 9 and SMA 26 of hl2) and above the SMA 20 and SMA 50 on volume 20 % above the previous bar's goes long; the mirror goes short; reversing.
Port of FMZ strategy #457812 "Cloud Momentum Crossover Strategy with Moving Averages and Volume Confirmation" (Ichimoku Clouds Strategy with Moving Averages and Volume Confirmation).

FMZ source id: 457812

Source
    https://www.fmz.com/strategy/457812 (PineScript v5, FMZ last modified 2024-07-26 17:38:28).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 166-206), conversion 9, base 26, span B 52 (SMAs of hl2), displacement 26 unused; SMA 20 / 50; volume threshold 20 %
    long_condition = close > span_a and close > sma20 and close > sma50 and volume > volume[1] x 1.2 -> entry Long
    short_condition = close < span_a and close < sma20 and close < sma50 and volume > volume[1] x 1.2 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "Ichimoku" lines are SMAs of hl2 (not mid-ranges) and span A is not displaced (the
      displacement input is unused), as written. Entries repeat while the conditions hold and add nothing.
      REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close above / below an undisplaced cloud line and two SMAs on rising volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.2 x the previous bar's; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_457812_sma_cloud_span_a_two_sma_volume_rise_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_ma": [20, 10],
    "vol_pct": [20.0, 50.0],
}
DEFAULT_PARAMS = {"conversion": 9, "base": 26, "fast_ma": 20, "slow_ma": 50, "vol_pct": 20.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    hl2 = (h + lo) / 2
    span_a = (hl2.rolling(int(p["conversion"])).mean() + hl2.rolling(int(p["base"])).mean()) / 2
    f, s = c.rolling(int(p["fast_ma"])).mean(), c.rolling(int(p["slow_ma"])).mean()
    vol_ok = v > v.shift(1) * (1 + float(p["vol_pct"]) / 100)
    lg = (c > span_a) & (c > f) & (c > s) & vol_ok
    sh = (c < span_a) & (c < f) & (c < s) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return lg.astype(bool), false, sh.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
