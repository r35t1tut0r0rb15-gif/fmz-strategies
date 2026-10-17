"""Smoothed Waddah explosions, long only, broker days: the one-bar rise of the MACD (20 / 40) of the Heikin Ashi close,
times 150, above the width of the 20-bar 1.5-sigma bands of ohlc4, with the RSI 14 over 40, goes long; the same size of
fall above the band width closes it.
Port of FMZ strategy #432237 "Dynamic Moving Average Trend Trading Strategy" (SmoothedWaddah).

FMZ source id: 432237

Source
    https://www.fmz.com/strategy/432237 (PineScript v5, FMZ last modified 2023-11-15 17:45:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 151-211), sensitivity 150, MACD 20 / 40, bands 20 x 1.5 on ohlc4, RSI filter 40
    t1 = (macd(ha_close) - macd(ha_close[1])) x 150;  e1 = upper(ohlc4, 20, 1.5) - lower(ohlc4, 20, 1.5)
    max(t1, 0) > e1 and rsi(close, 14) > 40 -> entry long;  max(-t1, 0) > e1 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Heikin Ashi close of the chart's own bar is its ohlc4 (request.security of the heikinashi
      ticker on the same timeframe, no look-ahead). macd(x[1]) is the MACD of the series one bar back,
      i.e. the previous MACD value. t2 is not used.
    * strategy.close('up', trendDown > e1) takes the condition as its when argument (v5 at the time).
      Long only; Opposite entries cannot occur. ta.stdev is the population deviation. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD change against the band width, RSI level.
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

NAME = "fmz_432237_smoothed_waddah_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sensitivity": [150, 75],
    "rsi_filter": [40, 50],
}
DEFAULT_PARAMS = {"sensitivity": 150, "fast": 20, "slow": 40, "bb_len": 20, "bb_mult": 1.5, "rsi_filter": 40}


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


def _rsi(x, n):
    d = x.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    o4 = (o + h + lo + c) / 4
    macd = o4.ewm(span=int(p["fast"]), adjust=False).mean() - o4.ewm(span=int(p["slow"]), adjust=False).mean()
    t1 = (macd - macd.shift(1)) * float(p["sensitivity"])
    e1 = 2 * float(p["bb_mult"]) * o4.rolling(int(p["bb_len"])).std(ddof=0)
    up = t1.clip(lower=0)
    dn = (-t1).clip(lower=0)
    le = ((up > e1) & (_rsi(c, 14) > float(p["rsi_filter"]))).astype(bool)
    lx = (dn > e1).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
