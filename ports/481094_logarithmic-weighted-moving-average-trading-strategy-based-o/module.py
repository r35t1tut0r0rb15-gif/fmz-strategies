"""Crossings of WMA 5 and WMA 20 of the log close (returned to price), broker days: the short crossing over the long goes long, crossing under goes short; reversing.
Port of FMZ strategy #481094 "Logarithmic-Weighted-Moving-Average-Trading-Strategy-Based-on-Cross-Signal-Analysis-基于对数加权移动平均交叉信号的量化交易策略" (Logaritmik WMA Al-Sat Stratejisi).

FMZ source id: 481094

Source
    https://www.fmz.com/strategy/481094 (PineScript v6, FMZ last modified 2025-02-08 14:53:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 79-130), WMA 5 / 20 of log(close), exp() back
    short = exp(wma(log(close), 5));  long = exp(wma(log(close), 20));  crossover -> entry AL;  crossunder -> entry SAT

Interpretation choices (Pine rules in SURVEY_README.md)
    * exp() is increasing, so the crossings are those of the log-price WMAs. REVERSAL INTENDED. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, log-price WMA crossings.
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

NAME = "fmz_481094_log_wma5_20_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [5, 10],
    "long_len": [20, 50],
}
DEFAULT_PARAMS = {"short_len": 5, "long_len": 20}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    lc = np.log(c)
    a = np.exp(_wma(lc, int(p["short_len"])))
    b = np.exp(_wma(lc, int(p["long_len"])))
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
