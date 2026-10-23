"""EMA 9 crossing EMA 20 of the close, broker days: crossing over goes long, crossing under goes short; reversing.
Port of FMZ strategy #428058 "Nine and Twenty Moving Average Crossover Strategy" (Dieyson daytrade EMA 9+20+200+VWAP and bar & line color).

FMZ source id: 428058

Source
    https://www.fmz.com/strategy/428058 (PineScript v1, FMZ last modified 2023-09-28 11:17:10).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 190-235), EMA 9 / 20 (EMA 200 and the VWAP only plotted); Pine version 1
    c = crossover(ema(close, 9), ema(close, 20)) and ema(9) > ema(20) -> entry COMPRA;  v = crossunder(ema(close, 9), ema(close, 20)) -> entry VENDA

Interpretation choices (Pine rules in SURVEY_README.md)
    * The VWAP, EMA 200 and the bar / line colours only feed plots, so volume does not reach the orders:
      ported as not using volume (check 8). REVERSAL INTENDED. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossover.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG428058 (2 members, best partner #431222, Jaccard 0.817); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428058_ema9_20_cross_daily_reversal"
FAMILY = "ma_crossover"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 20}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(subset=["close"])
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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
