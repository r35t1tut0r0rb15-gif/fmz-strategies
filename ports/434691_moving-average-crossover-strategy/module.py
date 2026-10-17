"""EMA 7 / 20 crosses confirmed by the close, broker days: the EMA 7 crossing above the EMA 20 on a bar closing above the
previous close goes long; the cross down on a bar closing below the previous close goes short (reversing).
Port of FMZ strategy #434691 "Moving Average Crossover Strategy" (Ma stratégie).

FMZ source id: 434691

Source
    https://www.fmz.com/strategy/434691 (PineScript v3, FMZ last modified 2023-12-08 12:20:42).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 148-202), EMA 7 / 20 on close, current resolution
    Uptrend = ema7 > ema20 and ema7[1] < ema20[1];  Buy = Uptrend and close > close[1] -> entry long
    Downtrend = ema7 < ema20 and ema7[1] > ema20[1];  Sell = Downtrend and close < close[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Use current timeframe" is on, so the security call is the chart's own close. The previous bar
      must be strictly on the other side, as written. strategy.entry reverses: REVERSAL INTENDED.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434691_ema_7_20_cross_confirmed"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [7, 14],
    "long_len": [20, 50],
}
DEFAULT_PARAMS = {"short_len": 7, "long_len": 20}


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
    s = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    lg = c.ewm(span=int(p["long_len"]), adjust=False).mean()
    upx = (s > lg) & (s.shift(1) < lg.shift(1))
    dnx = (s < lg) & (s.shift(1) > lg.shift(1))
    le = (upx & (c > c.shift(1))).astype(bool)
    se = (dnx & (c < c.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
