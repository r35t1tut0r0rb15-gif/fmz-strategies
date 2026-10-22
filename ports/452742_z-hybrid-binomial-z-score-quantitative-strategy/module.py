"""Extreme daily changes outside the Bollinger bands, daily bars, long only: a change whose 252-day z-score is under -1.5 with the close under the lower band (20 / 2) buys; a z-score over 1.5 with the close over the upper band sells.
Port of FMZ strategy #452742 "混合双态Z评分量化策略-Hybrid-Binomial-Z-Score-Quantitative-Strategy" (Estratégia Híbrida Quantitativa (z-score with Bollinger)).

FMZ source id: 452742

Source
    https://www.fmz.com/strategy/452742 (PineScript v5, FMZ last modified 2024-05-28 17:38:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-133), SMA 20, Bollinger 20 / 2; z-score of close - close[1] over 252 days; thresholds +- 1.5
    z < -1.5 and close < lower -> entry Long;  z > 1.5 and close > upper -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The z-score is of the one-bar price change against its own 252-bar mean and standard deviation.
      Both tests are states (a repeat entry while long is ignored); they cannot meet on one bar. Long
      only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, extreme-change dips below the band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_452742_change_zscore_bollinger_extreme_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [20, 50],
    "z_thr": [1.5, 2.0],
    "lookback": [252, 126],
}
DEFAULT_PARAMS = {"sma_len": 20, "z_thr": 1.5, "lookback": 252}


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
    n = int(p["sma_len"])
    basis, dev = c.rolling(n).mean(), 2 * c.rolling(n).std(ddof=0)
    ch = c.diff()
    k = int(p["lookback"])
    z = (ch - ch.rolling(k).mean()) / ch.rolling(k).std(ddof=0)
    t = float(p["z_thr"])
    le = (z < -t) & (c < basis - dev)
    lx = (z > t) & (c > basis + dev)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
