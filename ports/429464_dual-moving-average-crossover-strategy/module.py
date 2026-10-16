"""SMA-difference cross, long only, broker days: ohlc4 minus its SMA 50 crossing above the SMA 50 - SMA 100 spread
goes long, crossing below closes the long.
Port of FMZ strategy #429464 "Dual Moving Average Crossover Strategy" (SMA Diff strat).

FMZ source id: 429464

Source
    https://www.fmz.com/strategy/429464 (PineScript v3, FMZ last modified 2023-10-17 13:54:05).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 116-130), SMA 50 / 100 of ohlc4, smoothing 1
    dif = sma(ohlc4,50) - sma(ohlc4,100); out1 = ohlc4 - sma(ohlc4,50)
    crossover(out1, dif) -> entry long; crossunder(out1, dif) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both series are in price units but only their crossing is used: scale-free. The smoothed out3
      and out2 are drawn only.
    * Long only. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a cross of two series in the same units.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429464_sma_diff_cross_long"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [50, 20],
    "len2": [100, 200],
}
DEFAULT_PARAMS = {"len1": 50, "len2": 100}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + lo + c) / 4
    e1, e2 = src.rolling(int(p["len1"])).mean(), src.rolling(int(p["len2"])).mean()
    dif, out1 = e1 - e2, src - e1
    long_e = ((out1 > dif) & (out1.shift(1) <= dif.shift(1))).astype(bool)
    long_x = ((out1 < dif) & (out1.shift(1) >= dif.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
