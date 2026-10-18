"""Crossings of the smoothed OHLC average with a DEMA 34, broker days: the EMA 8 of ohlc4 crossing over the DEMA 34 closes any short and goes long; crossing under it closes any long and goes short
(reversing). The Williams %R, MACD, TSI and pivot blocks are only drawn.
Port of FMZ strategy #436479 "Dual MA Crossover Strategy" ([DS]Entry_Exit_TRADE.V01-Strategy).

FMZ source id: 436479

Source
    https://www.fmz.com/strategy/436479 (PineScript v4, FMZ last modified 2023-12-25 11:06:49).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 161-420), EMA 8 of ohlc4; DEMA 8 / 17 / 34 / 72 (only the 34 trades); the indicator blocks are off
    crossUP = crossover(ema(ohlc4, 8), dema34);  crossDN = crossunder(ema(ohlc4, 8), dema34);  from 2021: crossUP -> close Short, entry Long (1);  crossDN -> close Long, entry Short (1)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The explicit closes coincide with the reversal. The start date is the author's window: dropped. The
      fixed size 1 is sizing. REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crossing.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed order size stored.
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

NAME = "fmz_436479_ohlc4_ema_dema_cross"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dema_len": [34, 21],
    "ema_len": [8, 5],
}
DEFAULT_PARAMS = {"dema_len": 34, "ema_len": 8}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ohlc4 = (o + h + lo + c) / 4
    e_ohlc = ohlc4.ewm(span=int(p["ema_len"]), adjust=False).mean()
    n = int(p["dema_len"])
    e1 = c.ewm(span=n, adjust=False).mean()
    dema = 2 * e1 - e1.ewm(span=n, adjust=False).mean()
    le = ((e_ohlc > dema) & (e_ohlc.shift(1) <= dema.shift(1))).fillna(False).astype(bool)
    se = ((e_ohlc < dema) & (e_ohlc.shift(1) >= dema.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
