"""Double EMA position, broker days: the close over its DEMA 21 (and, if switched on, a positive MACD histogram) holds a long; the close at or under the
DEMA holds a short (reversing).
Port of FMZ strategy #436092 "DEMA策略MACD指标组合DEMA-MACD-Combination-Strategy" (DEMA Strategy with MACD).

FMZ source id: 436092

Source
    https://www.fmz.com/strategy/436092 (PineScript v1, FMZ last modified 2023-12-21 10:49:45).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 197-225), DEMA length 21; MACD 12 / 26 / 9; histogram filter off
    dema = 2 ema(close, 21) - ema(ema(close, 21), 21);  pos = close > dema ? 1 : 0;  entry long when pos == 1 and (macd histogram > 0 or the filter is off);  entry short when pos == 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are states re-sent every bar; vbt ignores a same-side signal. With the histogram
      filter on, a bar above the DEMA with a non-positive histogram gives no long entry (the
      position is kept). The date window is the author's (always true here): dropped. strategy.entry
      reverses: REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, DEMA position and a MACD filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436092_dema_position_macd_filter"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dema_length": [21, 34],
    "macd_control": [False, True],
}
DEFAULT_PARAMS = {"dema_length": 21, "macd_control": False}


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
    n = int(p["dema_length"])
    e1 = c.ewm(span=n, adjust=False).mean()
    dema = 2 * e1 - e1.ewm(span=n, adjust=False).mean()
    pos = (c > dema)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    macd_ok = (hist > 0) if p["macd_control"] else pd.Series(True, index=c.index)
    le = (pos & macd_ok & dema.notna()).fillna(False).astype(bool)
    se = ((~pos) & dema.notna()).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
