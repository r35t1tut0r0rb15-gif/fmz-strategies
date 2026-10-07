"""Hourly EMA(5) vs daily EMA(5) at each daily close: long when the hourly one is above,
short otherwise (always in).
Port of FMZ strategy #361360 "跨周期均线交易multiple-timeframe-trading".

Source
    https://www.fmz.com/strategy/361360 (PineScript, FMZ last modified 2022-05-06 16:47:08).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 26-38), chart period 1d
    expr = ta.ema(close, 5)                                    (daily)
    hVal = request.security(syminfo.tickerid, '60', expr)      (hourly EMA(5), lower timeframe)
    hVal > expr -> entry long, else -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * On a daily chart a lower-timeframe request returns the value of the day's last hourly bar,
      at the daily close: no lookahead. The port runs on 1-hour bars and signals only on the
      hourly bar that ends at the broker-day close (17:00 New York), where hourly EMA(5) and the
      daily EMA(5) (daily closes of broker days, today's close = that bar's close) are both
      known; it fills at the next hourly open, i.e. the next day's open, as the daily chart does.
      A day whose 16:00-17:00 bar is missing gives no signal.
    * strategy.entry every day in the current direction; a change of side reverses:
      REVERSAL INTENDED (portfolio_kwargs {}; the engine's default opposite-entry reversal).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361360_hourly_vs_daily_ema_side"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # daily chart (backtest 1d) reading 60-minute values: built from hourly bars
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [3, 5, 10, 20],
}
DEFAULT_PARAMS = {"ema_length": 5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["ema_length"])
    c = bars_df["close"]
    h_ema = c.ewm(span=n, adjust=False).mean().to_numpy()
    day = broker_day(bars_df.index)
    d_close = c.groupby(day).last()
    d_ema = d_close.ewm(span=n, adjust=False).mean().reindex(day).to_numpy()
    end_ny = (bars_df.index + pd.Timedelta(hours=1)).tz_convert("America/New_York")
    at_close = ((end_ny.hour == 17) & (end_ny.minute == 0)).astype(bool)
    n_days = pd.Series(1, index=d_close.index).cumsum().reindex(day).to_numpy()
    ready = at_close & (n_days >= n)

    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if not ready[i]:
            continue
        if h_ema[i] > d_ema[i]:
            if pos != 1:
                le[i], pos = True, 1
        elif pos != -1:
            se[i], pos = True, -1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
