"""WaveTrend gap turns, broker days, long only: the gap between the WaveTrend (10 / 21 on a 4-bar hlc3 average) and its 4-bar SMA rising goes long; falling closes.
Port of FMZ strategy #440866 "Trend Prediction Dual Moving Average Strategy" (BreakingDawn [JackTz]).

FMZ source id: 440866

Source
    https://www.fmz.com/strategy/440866 (PineScript v4, FMZ last modified 2024-02-02 17:39:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 139-170), channel 10, average 21; WT factor 4; years after 2016
    ap = sum(hlc3, 4) / 4;  wt1 = ema((ap - esa) / (0.015 d), 21);  wtAvg = wt1 - sma(wt1, 4);  buy = wtAvg[1] < wtAvg and wtAvg < close -> entry buy;  sell = wtAvg[1] > wtAvg -> close buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * "wtAvg < close" compares the oscillator with the price, so for prices above its range it always
      holds, as written. The year filter is dropped. Long only. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, WaveTrend gap slope.
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

NAME = "fmz_440866_wavetrend_gap_turn_long"
FAMILY = "wavetrend_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n1": [10, 20],
    "wt_factor": [4, 2],
}
DEFAULT_PARAMS = {"n1": 10, "wt_factor": 4, "n2": 21}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ap = ((h + lo + c) / 3).rolling(int(p["wt_factor"])).mean()
    n1 = int(p["n1"])
    esa = ap.ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    wt1 = ((ap - esa) / (0.015 * d.where(d > 0))).ewm(span=int(p["n2"]), adjust=False).mean()
    avg = wt1 - wt1.rolling(4).mean()
    buy = (avg.shift(1) < avg) & (avg < c)
    sell = avg.shift(1) > avg
    false = pd.Series(False, index=c.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
