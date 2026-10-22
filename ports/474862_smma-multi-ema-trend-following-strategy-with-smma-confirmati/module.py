"""EMA 10 / 22 crossings with a smoothed SMA 200 filter, 2-day bars: the cross up with the close over the filter goes long, the cross down under it goes short; reversing.
Port of FMZ strategy #474862 "多重均线趋势追踪与SMMA验证交易策略-Multi-EMA-Trend-Following-Strategy-with-SMMA-Confirmation" (EMA Crossover with SMMA and Additional EMAs).

FMZ source id: 474862

Source
    https://www.fmz.com/strategy/474862 (PineScript v5, FMZ last modified 2024-12-12 15:55:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-132), EMA 10 / 22; "SMMA" = SMA 2 of SMA 200; EMA 50 / 100 / 200 plotted only
    crossover(ema10, ema22) and close > sma(sma(close, 200), 2) -> entry Buy;  crossunder and close < it -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "SMMA" is the source's approximation, SMA 2 of SMA 200, as written. The extra EMAs are
      plotted only. There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing
      code. FREQ = "2D" from the backtest header (blocks of 2 broker days, as #429148).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with a long-average filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_474862_ema10_22_cross_smma200_filter_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [10, 5],
    "long_len": [22, 50],
}
DEFAULT_PARAMS = {"short_len": 10, "long_len": 22, "smma_len": 200, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    b = c.ewm(span=int(p["long_len"]), adjust=False).mean()
    f = c.rolling(int(p["smma_len"])).mean().rolling(2).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (c > f)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (c < f)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
