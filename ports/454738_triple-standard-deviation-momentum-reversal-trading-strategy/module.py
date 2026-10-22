"""Three-deviation band re-entries, daily bars, long only: the close crossing back over SMA 20 - 3 SD buys; crossing back under SMA 20 + 3 SD sells.
Port of FMZ strategy #454738 "Triple Standard Deviation Momentum Reversal Trading Strategy" (MikEy Scali 3 STD Dev Buy/Sell Strategy).

FMZ source id: 454738

Source
    https://www.fmz.com/strategy/454738 (PineScript v5, FMZ last modified 2024-06-21 14:44:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 151-195), SMA 20; 3 SD bands
    crossover(close, sma - 3 sd) -> entry Buy;  crossunder(close, sma + 3 sd) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, three-deviation band re-entries.
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

NAME = "fmz_454738_three_sd_band_reentry_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 3.0}


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
    n = int(p["length"])
    ma, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    k = float(p["mult"])
    up, lo = ma + k * sd, ma - k * sd
    c1 = c.shift(1)
    le = (c > lo) & (c1 <= lo.shift(1))
    lx = (c < up) & (c1 >= up.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
