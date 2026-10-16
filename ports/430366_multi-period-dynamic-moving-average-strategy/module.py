"""Close above an SMA 7, broker days, long only: a close above the SMA goes long, a close below it closes the long.
Port of FMZ strategy #430366 "Multi Period Dynamic Moving Average Strategy" (MA_strategy).

FMZ source id: 430366

Source
    https://www.fmz.com/strategy/430366 (PineScript v3, FMZ last modified 2023-10-27 16:07:16).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 174-236), SMA 7 (MA type option "SMA" by default)
    buy = close > ma -> entry long;  sell = close < ma -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The other MA types (EMA, TEMA, WMA, HMA) are options, not ported (default SMA). The 2017-2099
      test period is the author's window: dropped.
    * Long only; Opposite entries cannot occur. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: floor(equity / close) per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430366_close_above_sma_long"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [7, 20, 50],
}
DEFAULT_PARAMS = {"length": 7}


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
    ma = c.rolling(int(p["length"])).mean()
    false = pd.Series(False, index=bars_df.index)
    return (c > ma).astype(bool), (c < ma).astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
