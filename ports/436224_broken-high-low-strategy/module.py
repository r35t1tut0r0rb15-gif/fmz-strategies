"""Broken-candle entries with a fast-average exit, broker days, long only in effect: a green candle closing over the previous red candle's open in a rising fast / slow SMA pair (5 over 10) buys;
the "short" entry is also sent as a LONG order (the script passes strategy.long), so a red candle closing under the previous green candle's open in a falling pair also buys; each trade closes when
the close crosses its fast average the other way.
Port of FMZ strategy #436224 "Broken High Low Strategy" (Broken High/Low Strategy).

FMZ source id: 436224

Source
    https://www.fmz.com/strategy/436224 (PineScript v5, FMZ last modified 2023-12-22 12:59:43).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 155-227), fast SMA 5, slow SMA 10; EMA stop, opposing-bar exit, second entry and EOD close switches off; pyramiding 10, 25 % of equity
    longOpen = green candle and the previous candle red and close > open[1] and fastMA > slowMA -> entry "Long Entry" (long);  longClose = crossunder(close, fastMA) -> close "Long Entry"
    shortOpen = red candle and the previous candle green and close < open[1] and fastMA < slowMA -> strategy.entry("Short Entry", strategy.LONG);  shortClose = crossover(close, fastMA) -> close "Short Entry"

Interpretation choices (Pine rules in SURVEY_README.md)
    * The second entry id is declared with strategy.long, so both ids open long trades; each is closed by
      its own rule (strategy.close by id). The two trades are of the same direction: the port holds one
      long position while either is open (the stacked size, pyramiding 10, is sizing). The date window,
      the EMA stop, the opposing-bar exit, the second-bar entry and the end-of-day close are off or
      the author's window. Long only. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, both ids long; stacked trades held as one position.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and pyramiding stored.
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

NAME = "fmz_436224_broken_candle_two_ids_long"
FAMILY = "candle_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_ma": [5, 8],
    "slow_ma": [10, 20],
}
DEFAULT_PARAMS = {"fast_ma": 5, "slow_ma": 10}


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
    o, c = bars_df["open"], bars_df["close"]
    fast = c.rolling(int(p["fast_ma"])).mean()
    slow = c.rolling(int(p["slow_ma"])).mean()
    green, red = c > o, c < o
    prior_red, prior_green = c.shift(1) < o.shift(1), c.shift(1) > o.shift(1)
    a_open = (green & prior_red & (c > o.shift(1)) & (fast > slow)).fillna(False).to_numpy()
    b_open = (red & prior_green & (c < o.shift(1)) & (fast < slow)).fillna(False).to_numpy()
    a_close = ((c < fast) & (c.shift(1) >= fast.shift(1))).fillna(False).to_numpy()
    b_close = ((c > fast) & (c.shift(1) <= fast.shift(1))).fillna(False).to_numpy()
    m = len(a_open)
    held = np.zeros(m, dtype=np.int8)
    a = b = False                                  # the two long trades by id
    pend = None
    for i in range(m):
        if i > 0 and pend is not None:             # fills at this bar's open, in the script's call order
            ea, ca, eb, cb = pend
            if ea:
                a = True
            if ca:
                a = False
            if eb:
                b = True
            if cb:
                b = False
        held[i] = 1 if (a or b) else 0
        pend = (bool(a_open[i]), bool(a_close[i]), bool(b_open[i]), bool(b_close[i]))
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
