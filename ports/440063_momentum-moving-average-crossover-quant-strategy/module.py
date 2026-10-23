"""Hourly bars: the SMA 9 crossing over the SMA 21 while the last day's volume is under half the (7-bar average of the) last week's volume goes long; the SMA 9 crossing under the SMA 21 goes short; reversing.
Port of FMZ strategy #440063 "Momentum Moving Average Crossover Quant Strategy" (MA and Volume Strategy).

FMZ source id: 440063

Source
    https://www.fmz.com/strategy/440063 (PineScript v5, FMZ last modified 2024-01-26 11:39:26).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 156-182), SMA 9 / 21; volume threshold 50 %; daily and weekly security() volume
    dailyVolume = security("D", volume);  weeklyVolumeAvg = sma(security("W", volume), 7)
    crossover(fastMA, slowMA) and dailyVolume < weeklyVolumeAvg * 50 / 100 -> entry Long;  crossunder -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * security() without lookahead gives, on historical bars, the last completed day's / week's
      volume (the current one only on its last bar); the port uses the last completed broker day and
      broker week (Monday-start weeks of broker days) throughout (as earlier ports). The SMA 7 runs over
      the chart's bars, so it is the weekly value averaged over the last 7 hours (weird case). A day's
      volume is usually far below half a week's, so the filter rarely blocks. The take-profit / stop
      levels are only plotted. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with a daily-versus-weekly volume filter on longs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data) summed per broker day and per broker week; exchange volume to be compared later (Austin, 2026-10-23).
Session open: last completed broker day / broker week (17:00 America/New_York) for the volumes.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440063_sma9_21_cross_day_vs_week_volume_filter_1h_reversal"
FAMILY = "volume_filter"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vol_pct": [50, 25],
    "fast": [9, 5],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "vol_pct": 50}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    day = broker_day(c.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")
    dvol = v.groupby(day).sum().shift(1)                  # the last COMPLETED broker day
    wvol = v.groupby(week).sum().shift(1)                 # the last COMPLETED broker week
    d_now = pd.Series(dvol.reindex(day).to_numpy(), index=c.index)
    w_now = pd.Series(wvol.reindex(week).to_numpy(), index=c.index).rolling(7).mean()
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    co = (f > s) & (f.shift(1) <= s.shift(1))
    cu = (f < s) & (f.shift(1) >= s.shift(1))
    le = co & (d_now < w_now * float(p["vol_pct"]) / 100)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return le.astype(bool), false, cu.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
