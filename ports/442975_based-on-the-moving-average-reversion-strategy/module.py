"""PJ Sutherland's Jaws mean reversion, daily bars, long only: the SMA 2 crossing under 97 % of the SMA 5 goes long; the SMA 2 crossing back over the SMA 5 closes.
Port of FMZ strategy #442975 "Based on the Moving Average Reversion Strategy" (Jaws Mean Reversion [Strategy]).

FMZ source id: 442975

Source
    https://www.fmz.com/strategy/442975 (PineScript v4, FMZ last modified 2024-02-27 17:51:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 144-176), SMA 2 / 5 of the close; 3 % below to buy
    buyMA = 0.97 sma(close, 5);  crossunder(sma2, buyMA) -> entry BUY;  crossover(sma2, sma5) -> close BUY

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, short / long SMA gap.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442975_jaws_sma2_under_sma5_gap_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "big": [5, 10],
    "pct_below": [3.0, 5.0],
}
DEFAULT_PARAMS = {"big": 5, "pct_below": 3.0, "small": 2}


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
    sm = c.rolling(int(p["small"])).mean()
    bg = c.rolling(int(p["big"])).mean()
    buy = bg * (100 - float(p["pct_below"])) / 100
    le = (sm < buy) & (sm.shift(1) >= buy.shift(1))
    lx = (sm > bg) & (sm.shift(1) <= bg.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
