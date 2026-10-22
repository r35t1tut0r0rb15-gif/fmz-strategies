"""Bullish engulfing-style candles on a rising last 15-minute close, broker days, long only: the signal goes long with the previous bar's low as stop and a 2R target from the signal close.
Port of FMZ strategy #485292 "Multi Timeframe Trend Recognition and Candlestick Pattern Trading Strategy" (Multi-Timeframe Strategy with Time Filters).

FMZ source id: 485292

Source
    https://www.fmz.com/strategy/485292 (PineScript v5, FMZ last modified 2025-03-07 09:57:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 164-207), security("15", close); engulfing; stop low[1]; target 2R; time filters at 9:00-9:45 and 15:00-16:59; close-all at 16:00; 10 % of equity
    bullish = close > open and open[1] > close[1] and close > open[1];  long = bullish and security("15", close) > security("15", close)[1] and not restricted -> entry Long, stop := low[1], tp := close + 2 (close - low[1])
    every bar: exit Long (stop, limit);  hour == 16 and minute == 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * "15" is a lower time frame than the daily chart, requested without lookahead: each day gets its
      last 15-minute close, which is the day's close (as #436765), so the trend test reads close >
      close[1]. The clock tests read the bar's time; a daily bar is stamped at its start, so the hour 9 /
      15 / 16 windows and the 16:00 close-all never fire on daily bars, as written (as the C170-C175
      readings).
    * The levels are stored at the signal and re-sent every bar unchanged; they are sent as fractions of
      the fill open (a level at or through it is marketable and closed one bar late, as #458256). A
      repeat signal while held stores new levels; stops() keeps the first, so the repeat case is marked
      trailing_stop_pending (as #434428). Long only; Opposite entries cannot occur. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The 10 % of equity size
      is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; previous-bar stop and 2R target as fractions of the fill.
    2 generic: PASS, engulfing candles on a rising close.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); the clock filters never fire on daily bars.
Long only. Opposite entries cannot occur.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_485292_engulf_rising_close_prev_low_stop_2r_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [2.0, 3.0, 1.5],
}
DEFAULT_PARAMS = {"rr": 2.0}


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


def _signals(bars_df, p):
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    eng = (c > o) & (o.shift(1) > c.shift(1)) & (c > o.shift(1))
    le = eng & (c > c.shift(1))
    sl = lo.shift(1)
    return le, {"l_sl": sl, "l_tp": c + float(p["rr"]) * (c - sl)}


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    false = pd.Series(False, index=o.index)
    return le, lf & l_thr & ~le, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    sl_f = 1 - lvl["l_sl"].shift(1) / o
    tp_f = lvl["l_tp"].shift(1) / o - 1
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
