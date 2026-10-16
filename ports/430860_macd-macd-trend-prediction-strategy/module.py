"""Zero-lag (DEMA) MACD, broker days, long only: the zero-lag MACD line above its zero-lag signal goes long, below it
closes the long.
Port of FMZ strategy #430860 "MACD趋势预测策略MACD-Trend-Prediction-Strategy" (MACD Trendprediction Strategy V1).

FMZ source id: 430860

Source
    https://www.fmz.com/strategy/430860 (PineScript v4, FMZ last modified 2023-11-02 15:25:11).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 158-194), DEMA 12 / 26, signal DEMA 9
    line = DEMA(close, 12) - DEMA(close, 26); signal = DEMA(line, 9)   (DEMA = 2 ema - ema(ema))
    line > signal -> entry long;  line < signal -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.close("Buy", strategy.long, ...) passes strategy.long as the "when" argument (true),
      inside the if: a plain close. Long only; Opposite entries cannot occur. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, zero-lag moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430860_zero_lag_macd_long"
FAMILY = "macd_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 50],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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


def _dema(x, n):
    e = x.ewm(span=n, adjust=False).mean()
    return 2 * e - e.ewm(span=n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    line = _dema(c, int(p["fast"])) - _dema(c, int(p["slow"]))
    sig = _dema(line, int(p["signal"]))
    false = pd.Series(False, index=bars_df.index)
    return (line > sig).astype(bool), (line < sig).astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
