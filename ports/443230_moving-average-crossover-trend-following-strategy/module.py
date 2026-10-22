"""SMA 100 / 200 crossings of the day's last 4-hour values, daily bars: the 4-hour SMA 100 crossing over the SMA 200 (as read at the end of each day) goes long, under goes short; reversing.
Port of FMZ strategy #443230 "Moving Average Crossover Trend Following Strategy" (MA Crossover Strategy).

FMZ source id: 443230

Source
    https://www.fmz.com/strategy/443230 (PineScript v5, FMZ last modified 2024-03-01 10:59:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-138), SMA 200 / 100 on 240 minutes
    ma200 = security(240, sma(close, 200));  ma100 = security(240, sma(close, 100));  crossover(ma100, ma200) -> entry Long, close Short;  crossunder -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 240-minute request from a daily chart is a lower time frame: its value is the day's last
      4-hour bar (as #436765), with the 4-hour bars counted from the broker day's start (six per day),
      built from minutes in precompute. The closes repeat the reversals. strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 4-hour values end with the day.
    2 generic: PASS, lower-time-frame SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443230_last_4h_sma100_200_cross_daily_reversal"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [100, 50],
    "slow": [200, 400],
}
DEFAULT_PARAMS = {"fast": 100, "slow": 200}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    # 4-hour bars counted from each broker day's start (17:00 America/New_York): six per day
    ny = df.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)
    blk = np.asarray((ny - ny.normalize()) // pd.Timedelta(minutes=240))
    c4 = df["close"].groupby([lab, blk]).last()
    day4 = c4.index.get_level_values(0)
    s4 = pd.Series(c4.to_numpy(), index=pd.RangeIndex(len(c4)))
    for col, n in (("sma_f", int(p["fast"])), ("sma_s", int(p["slow"]))):
        v = s4.rolling(n).mean().to_numpy()
        last = pd.Series(v, index=day4)
        last = last[~day4.duplicated(keep="last")]           # the day's last 4-hour bar
        bars[col] = last.reindex(bars.index).to_numpy()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    a, b = bars_df["sma_f"], bars_df["sma_s"]
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=a.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
