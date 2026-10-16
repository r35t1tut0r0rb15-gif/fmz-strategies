"""Ichimoku TK state above the EMA 200, broker days, long only: the conversion line (20) above the base line (60) with the
close above the EMA 200 goes long; the conversion line under the base line closes it.
Port of FMZ strategy #430142 "Ichimoku Balance Line trend following Strategy" (TK Cross > EMA200 Strat).

FMZ source id: 430142

Source
    https://www.fmz.com/strategy/430142 (PineScript v3, FMZ last modified 2023-10-25 14:32:23).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 175-204), conversion 20, base 60, EMA 200
    conversion = avg(lowest(20), highest(20)); base = avg(lowest(60), highest(60))
    conversion > base and close > ema(close, 200) -> entry long;  conversion < base -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lead lines and the lagging span only plot. Long only; Opposite entries cannot occur.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel midpoints and a moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: initial_capital / close per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430142_tk_state_above_ema200_long"
FAMILY = "ichimoku"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion": [20, 9],
    "base": [60, 26],
}
DEFAULT_PARAMS = {"conversion": 20, "base": 60, "ema_len": 200}


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
    a, b = int(p["conversion"]), int(p["base"])
    conv = (lo.rolling(a).min() + h.rolling(a).max()) / 2
    base = (lo.rolling(b).min() + h.rolling(b).max()) / 2
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    long_e = ((conv > base) & (c > ema)).astype(bool)
    long_x = (conv < base).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
