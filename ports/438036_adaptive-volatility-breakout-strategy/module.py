"""Range breakouts held one day, broker days, long only: from flat, a high above the previous close plus 0.6 of the previous day's log range (taken back with base 2.718) buys; the next bar closes it.
Port of FMZ strategy #438036 "Adaptive Volatility Breakout Strategy" (Volatility Breakout Strategy).

FMZ source id: 438036

Source
    https://www.fmz.com/strategy/438036 (PineScript v5, FMZ last modified 2024-01-08 14:38:31).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 153-173), k 0.6; daily security on a 1-day chart; 100 % of equity
    lp = log(c[1]) + (log(h[1]) - log(l[1])) x 0.6;  _lp = 2.718 ^ lp;  _lp < high and opentrades == 0 -> entry Long;  exit = hour == 0 or log(close) < (log(l[1]) + lp) / 2 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * security("D", ...) on a daily chart returns the chart's own bars. hour == 0 holds on every daily bar
      (each day bar opens at the session start of FMZ's UTC days), so the exit is true on every bar: a
      trade is closed at the close of the bar after its signal (it lives one bar, from the next open to
      the open after), as written (owed: probably for an intraday chart). The base 2.718 for e is kept.
      Closes act on the position held at the bar close; the entry only from flat. Long only. The 100 % of
      equity size is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, log-range breakout level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); hour == 0 read as every daily bar.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438036_log_range_breakout_one_day"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "k": [0.6, 0.4, 0.8, 0.5],
}
DEFAULT_PARAMS = {"k": 0.6}


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
    lp = np.log(c.shift(1)) + (np.log(h.shift(1)) - np.log(lo.shift(1))) * float(p["k"])
    level = np.power(2.718, lp)
    lc = (level < h).to_numpy()
    ex = np.ones(len(c), dtype=bool) | (np.log(c) < (np.log(lo.shift(1)) + lp) / 2).to_numpy()   # hour == 0
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend_e, pend_x = 0, False, False
    for i in range(m):
        if pend_x:                                       # orders of the last bar fill at this open
            pos, pend_x = 0, False
        if pend_e:
            pos, pend_e = 1, False
        if pos == 0 and lc[i] and i + 1 < m:
            le[i], pend_e = True, True
        elif pos == 1 and ex[i]:
            lx[i], pend_x = True, True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
