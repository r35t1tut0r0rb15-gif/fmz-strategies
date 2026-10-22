"""Close crossing its SMA 21, daily bars, long only: the close crossing over the SMA 21 goes long, crossing under closes.
Port of FMZ strategy #442558 "基于价格与SMA交叉的量化交易策略Quantitative-Trading-Strategy-Based-on-Price-Crossover-with-SMA" (Price Cross Above/Below SMA Strategy (Tressy Strat)).

FMZ source id: 442558

Source
    https://www.fmz.com/strategy/442558 (PineScript v5, FMZ last modified 2024-02-22 17:34:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 129-186), SMA 21 (50 / 200 plots only); daily close via request.security on the daily chart; dates 2022 (filter_condition true)
    filtered_close = request.security(tickerid, "D", close[0], lookahead_on);  crossover(filtered_close, sma(filtered_close, 21)) -> entry Buy;  crossunder -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The chart is daily, so the daily request returns the chart's own close (no look-ahead on the same
      time frame). The date filter is set to true in the source. The SMA 50 / 200 only plot. Long only.
      No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close vs SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442558_close_sma21_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_length": [21, 50],
}
DEFAULT_PARAMS = {"sma_length": 21}


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
    s = c.rolling(int(p["sma_length"])).mean()
    le = (c > s) & (c.shift(1) <= s.shift(1))
    lx = (c < s) & (c.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
