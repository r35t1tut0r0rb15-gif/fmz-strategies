"""Weekly regime filter (long only): in the market while this week's high breaks the prior
20-week high or this week's low holds above the 10-week MA; out when the low breaks the MA.
Port of FMZ strategy #271523 "韭菜保护程序唐安奇通道均仓策略" (Donchian / balanced-position
"retail protection" strategy).

Source
    https://www.fmz.com/strategy/271523 (Python, author "去者伯仁", FMZ last modified
    2021-07-20 17:27:39). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 79-181)
    week_kline = daily records composed 7 at a time; [-1] is the current (partial) week
    if week[-1].High > TA.Highest(week, 20, 'High')                    -> '全仓' (all in)
    elif week[-1].High < Highest20 and week[-1].Low > TA.MA(week,10)[-1] -> '均仓' (keep 50/50)
    elif week[-1].Low < MA10                                          -> '空仓' (all out)
    (any other case, e.g. equalities, also sells everything)

Interpretation choices
    * Exposure levels 100 % / 50 % are sizing (criterion 4); the signal is "in the market" for
      全仓 and 均仓 and "out" otherwise. From flat, 均仓 buys back to 50 %, so it is an entry too.
    * Bars: daily broker days (17:00 New York); evaluated on each completed day t, with the
      current week to date (days of t's week up to t) as week[-1]. Weeks are calendar weeks of
      the broker-day dates; the source's "7 daily records" groups are crypto weeks anchored at
      the first record of FMZ's window, which has no stable meaning for 5-day markets.
    * TA.Highest excludes the current week (SURVEY_README FMZ TA rule): the prior 20 completed
      weeks. TA.MA(week,10)[-1] includes the current partial week's close.
    * The source treats fewer than 21 weeks as 均仓 (in the market); the port emits nothing
      until 20 completed weeks exist (warm-up), which only matters at the start of the data.
    * Long only (spot); shorts are never emitted, so opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_271523_weekly_breakout_ma_regime_long"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # code reads PERIOD_D1 records and composes weeks (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hh_weeks": [10, 20, 30],
    "ma_weeks": [5, 10, 20],
}
DEFAULT_PARAMS = {"hh_weeks": 20, "ma_weeks": 10}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    nh, nm = int(p["hh_weeks"]), int(p["ma_weeks"])
    day = broker_day(bars_df.index)                       # session end date of each daily bar
    week = np.asarray(day - pd.to_timedelta(day.weekday, unit="D"))   # Monday of that week
    df = pd.DataFrame({"week": week, "high": bars_df["high"].to_numpy(),
                       "low": bars_df["low"].to_numpy(), "close": bars_df["close"].to_numpy()})
    wtd_high = df.groupby("week")["high"].cummax().to_numpy()   # current week to date
    wtd_low = df.groupby("week")["low"].cummin().to_numpy()
    close = df["close"].to_numpy()
    weekly = df.groupby("week").agg(high=("high", "max"), close=("close", "last"))
    prior_hh = weekly["high"].rolling(nh).max().shift(1)        # completed weeks before this one
    prior_close_sum = weekly["close"].rolling(nm - 1).sum().shift(1)
    hh = prior_hh.reindex(week).to_numpy()
    ma = ((prior_close_sum.reindex(week).to_numpy() + close) / nm) if nm > 1 else close

    full = wtd_high > hh
    balanced = (wtd_high < hh) & (wtd_low > ma)
    in_market = full | balanced
    ready = ~np.isnan(hh) & ~np.isnan(ma)

    m = len(close)
    entries, exits = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    in_pos = False
    for i in range(m):
        if not ready[i]:
            continue
        if in_market[i] and not in_pos:
            entries[i], in_pos = True, True
        elif not in_market[i] and in_pos:
            exits[i], in_pos = True, False

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(entries, index=idx), pd.Series(exits, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
