"""SMA alignment, daily bars, long only (spot): the SMA 20 (the Bollinger basis) over the SMA 34 over the SMA 89 buys; the SMA 20 under the SMA 34 sells.
Port of FMZ strategy #452615 "布林带RSI多均线趋势策略-Bollinger-Bands-RSI-Multi-MA-Trend-Strategy" (Bollinger Bands + RSI Strategy with MA).

FMZ source id: 452615

Source
    https://www.fmz.com/strategy/452615 (PineScript v5, FMZ last modified 2024-05-27 15:20:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-183), SMA 20 basis; SMA 34 / 89 (144 / 233 / 377 / 610 plotted only); quantity 1.0 / 0.5 / 0 by condition
    basis > sma34 and sma34 > sma89 -> entry Buy (qty 1.0);  basis < sma34 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both tests are states (a repeat entry while long is ignored). The quantity rule (1.0, or 0.5 /
      0 when the basis is under the SMA 34) only changes the size, and an entry always comes with
      the basis over the SMA 34, so it is sizing (stored). The RSI and MACD 'divergence' signals and
      the longer SMAs are only plotted. Spot account: Long only. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA alignment state.
    3 crypto-exchange-only: no (spot pair in the header only).
    4 signals only: the quantity rule stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_452615_sma20_34_89_alignment_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "basis_len": [20, 10],
    "mid_len": [34, 50],
    "slow_len": [89, 144],
}
DEFAULT_PARAMS = {"basis_len": 20, "mid_len": 34, "slow_len": 89}


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
    b = c.rolling(int(p["basis_len"])).mean()
    m34 = c.rolling(int(p["mid_len"])).mean()
    m89 = c.rolling(int(p["slow_len"])).mean()
    false = pd.Series(False, index=bars_df.index)
    return (b > m34) & (m34 > m89), b < m34, false, false.copy()


def portfolio_kwargs(**params):
    return {}
