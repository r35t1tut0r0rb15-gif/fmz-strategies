"""Bollinger 20 / 2 breakouts, broker days, long only: a close above the upper band buys, a close below the lower band closes.
Port of FMZ strategy #477579 "Bollinger Bands Breakout Momentum Trading Strategy" (Demo GPT - Bollinger Bands Strategy).

FMZ source id: 477579

Source
    https://www.fmz.com/strategy/477579 (PineScript v5, FMZ last modified 2025-01-06 15:19:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-138), BB 20 / 2, basis SMA; qty 1; capital 100000; commission 0.1 %, slippage 3
    close > upper -> entry Long (qty 1);  close < lower -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default SMA basis is ported; the other MA types are not swept. The entry repeats while the
      close stays above the band and is ignored while long. Long only. The fixed qty and capital are
      sizing; the commission and slippage settings are costs and are not ported (house cost model).
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger band breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 and capital 100000 stored, not ported; costs not ported.
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

NAME = "fmz_477579_bb20_upper_break_lower_close_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


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
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    le = c > basis + dev
    lx = c < basis - dev
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
