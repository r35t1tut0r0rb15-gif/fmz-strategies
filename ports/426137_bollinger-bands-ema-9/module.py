"""Bollinger + EMA 9 (long only): after a close below the lower band (20, 2 sd) go long; a close at or
above EMA 9 closes it.
Port of FMZ strategy #426137 "Bollinger Bands + EMA 9".

Source
    https://www.fmz.com/strategy/426137 (PineScript v5, FMZ last modified 2023-09-08 16:00:29).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 63-82), BB 20 x 2 on close, EMA 9
    close[1] < lower -> entry long (qty 1);  close >= ema9 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close does not apply on the bar its own entry is placed (position mirrored in
      simulate()); an entry while long is ignored. Population stdev.
    * Long only, as written (rule 6); upon_opposite_entry="ignore".
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426137_bb_lower_ema9_exit_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "mult": [1.5, 2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "ema_len": 9}


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
    c = bars_df["close"]
    n = int(p["length"])
    lower = c.rolling(n).mean() - p["mult"] * c.rolling(n).std(ddof=0)
    entry = (c.shift(1) < lower).to_numpy()
    out = (c >= c.ewm(span=int(p["ema_len"]), adjust=False).mean()).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and entry[i]:
            le[i], pos = True, 1
        elif pos == 1 and out[i]:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
