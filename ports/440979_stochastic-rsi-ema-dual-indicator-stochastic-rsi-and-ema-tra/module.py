"""Close stochastic dips in an EMA uptrend, broker days, long only: the 3-day SMA of the 14-day stochastic of the close under 20 with the EMA 55 above the EMA 200 goes long; above 80 closes.
Port of FMZ strategy #440979 "双重指标的Stochastic-RSI和EMA交易策略Dual-Indicator-Stochastic-RSI-and-EMA-Trading-Strategy" (StochRSI & EMA).

FMZ source id: 440979

Source
    https://www.fmz.com/strategy/440979 (PineScript v4, FMZ last modified 2024-02-04 15:00:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-164), stochastic of close 14, K 3, D 3 (plotted); EMA 55 / 200; levels 20 / 80
    k = sma(stoch(close, close, close, 14), 3);  buy = k < 20 and ema55 > ema200 -> entry Buy;  sell = k > 80 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Despite its name the oscillator is the stochastic of the close itself (no RSI). The buy and sell
      tests cannot hold together. Long only. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic of the close and EMA trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_440979_close_stoch_dip_ema_trend_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stoch_length": [14, 7],
    "ema1_period": [55, 34],
}
DEFAULT_PARAMS = {"stoch_length": 14, "ema1_period": 55, "k_period": 3, "ema2_period": 200}


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
    n = int(p["stoch_length"])
    ll, hh = c.rolling(n).min(), c.rolling(n).max()
    k = (100.0 * (c - ll) / (hh - ll).where(hh > ll)).rolling(int(p["k_period"])).mean()
    e1 = c.ewm(span=int(p["ema1_period"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ema2_period"]), adjust=False).mean()
    buy = (k < 20) & (e1 > e2)
    sell = k > 80
    false = pd.Series(False, index=c.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
