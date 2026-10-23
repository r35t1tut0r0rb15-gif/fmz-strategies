"""Breaks of the previous day's last-hour close by 60 points, read on each day's last hourly block, broker days: a last-hour high over the previous value plus 60 points goes long, a last-hour low under it minus 60 points goes short; reversing (a bar doing both ends short).
Port of FMZ strategy #453281 "Dynamic Timeframe High Low Breakout Strategy" (NIFTY 65-15).

FMZ source id: 453281

Source
    https://www.fmz.com/strategy/453281 (PineScript v5, FMZ last modified 2024-06-03 17:01:06).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 83-118), points 60; timeframe "60" (request.security high / low / close, no lookahead) on the daily header chart
    buy = security("60", high) > security("60", close)[1] + 60;  sell = security("60", low) < security("60", close)[1] - 60
    buy -> entry Buy;  sell -> entry Sell;  sell -> close Buy;  buy -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Reopened by Austin on 2026-10-23: the C192 rejection read the "60" request as undefined, but a
      lower time frame without lookahead returns the chart bar's last block (#436765, #477605), so each
      daily bar uses the high, low and close of its last hourly block, built from the minutes in
      precompute (hours counted from the broker-day start); [1] is the previous daily bar's value. The
      60 points are a price amount, read as a fraction of 42000 of that previous close (1.429e-03). The
      calls run in source order, as #453276: entries first (an entry on the held side ignored, the later
      call winning a same-bar tie, as #437773), then the closes, which act only on the trade held into
      the bar when no earlier call reversed it. REVERSAL INTENDED. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; lower-time-frame values from each day's last hourly block.
    2 generic: PASS, last-hour breaks of the previous last-hour close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: ND453276 (2 members, best partner #453276, Jaccard 0.676); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); last hourly block of each day.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453281_last_hour_break_prev_last_hour_close_points_reversal"
FAMILY = "momentum_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "points_frac": [1.428571e-03, 5e-03, 1e-02],
}
DEFAULT_PARAMS = {"points_frac": 1.428571e-03, "block_minutes": 60}


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
    n = int(p["block_minutes"])
    ltf = df.resample(f"{n}min", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    last = ltf.groupby(broker_day(ltf.index)).tail(1)               # the day's last block
    last.index = broker_day(last.index)
    for k in ("high", "low", "close"):
        bars[f"ltf_{k}"] = last[k].reindex(bars.index).to_numpy()
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["ltf_high"], bars_df["ltf_low"], bars_df["ltf_close"]
    c1 = c.shift(1)
    d = c1 * float(p["points_frac"])
    buy = (h > c1 + d).to_numpy()
    sell = (lo < c1 - d).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if buy[i] and cur != 1:
            cur = 1
        if sell[i] and cur != -1:
            cur = -1
        if sell[i] and pos == 1 and cur == 1:
            cur = 0
        if buy[i] and pos == -1 and cur == -1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
