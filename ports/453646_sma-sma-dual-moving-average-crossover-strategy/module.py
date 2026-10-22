"""SMA 50 / 200 golden and death crosses, daily bars, long only: the golden cross buys, the death cross sells.
Port of FMZ strategy #453646 "SMA双均线交叉策略-SMA-Dual-Moving-Average-Crossover-Strategy" (SMA Crossover Strategy with Date Range and Timeframe).

FMZ source id: 453646

Source
    https://www.fmz.com/strategy/453646 (PineScript v5, FMZ last modified 2024-06-07 14:49:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-124), SMA 50 / 200 on timeframe 'D' (the chart's own); date range on the markers only; quantity 1, commission 0
    crossover(sma50, sma200) -> entry Buy;  crossunder -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security on 'D' on the daily header chart returns the chart's own averages. The date
      range only gates the plotted markers, not the orders. Long only. The fixed quantity 1 is sizing.
      FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, golden / death crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453646_sma50_200_golden_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [50, 20],
    "long_len": [200, 100],
}
DEFAULT_PARAMS = {"short_len": 50, "long_len": 200}


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
    a = c.rolling(int(p["short_len"])).mean()
    b = c.rolling(int(p["long_len"])).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    lx = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
