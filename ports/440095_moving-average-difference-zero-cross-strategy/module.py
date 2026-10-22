"""Close-to-EMA 8 distance turns, long only, broker days: the close's distance from the EMA 8 turning up while under the EMA's rise above its 8-bar low goes long; the written exit places nothing, so the long is
held to the end of the data, as written.
Port of FMZ strategy #440095 "Moving Average Difference Zero Cross Strategy" (Estratégia diferença menor preço de 8).

FMZ source id: 440095

Source
    https://www.fmz.com/strategy/440095 (PineScript v4, FMZ last modified 2024-01-26 15:45:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-137), EMA 8 (fixed in the code)
    diff = close - ema8;  diff1 = close[1] - ema(close[1], 8);  diffLow = ema8 - lowest(ema8, 8);  buy = diff < diffLow and crossover(diff, diff1) -> entry Buy
    sell = diff > 0 and diff < diffLow and crossunder(diff, diff1) -> strategy.exit("Buy") with no levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * ema(close[1], 8) is the EMA of the previous closes. The exit call has no profit, loss, stop, limit
      or trail, so it places no order: after the first buy the long is held to the end of the data (as
      #439111; the intended close is owed). One position is held. Long only. No sizing code. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA distance turns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: DG440095 (2 members, best partner #439706, Jaccard 0.805); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440095_ema8_distance_turn_held_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_period": [8, 13],
}
DEFAULT_PARAMS = {"ema_period": 8}


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
    n = int(p["ema_period"])
    e = c.ewm(span=n, adjust=False).mean()
    e1 = c.shift(1).ewm(span=n, adjust=False).mean()
    d = c - e
    d1 = c.shift(1) - e1
    dl = e - e.rolling(n).min()
    buy = ((d < dl) & (d > d1) & (d.shift(1) <= d1.shift(1))).to_numpy()
    hits = np.flatnonzero(buy[:-1])
    le = np.zeros(len(c), dtype=bool)
    if len(hits):
        le[hits[0]] = True                               # one long, held to the end
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
