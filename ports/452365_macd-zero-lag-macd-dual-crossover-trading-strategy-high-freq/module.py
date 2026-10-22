"""Zero-lag MACD 12 / 26 / 9 crossings, daily bars: the MACD crossing its zero-lag signal upward below zero goes long, downward above zero goes short; reversing.
Port of FMZ strategy #452365 "MACD双转换零滞后交易策略-基于短期趋势捕捉的高频交易-Zero-Lag-MACD-Dual-Crossover-Trading-Strategy-High-Frequency-Trading-Based-on-Short-Term-Trend-Capture" (BNM INTRADAY SETUP MACD 3M - Version 1.2 (Zero Lag MACD Enhanced 1.2)).

FMZ source id: 452365

Source
    https://www.fmz.com/strategy/452365 (PineScript v4, FMZ last modified 2024-05-24 18:14:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-160), zero-lag EMA 12 / 26 (2 x EMA - EMA of EMA); signal 2 x EMA 9 - EMA of EMA 9 (useOldAlgo false)
    cross(zlmacd, signal) and hist > 0 and zlmacd < 0 -> entry Buy;  cross(zlmacd, signal) and hist <= 0 and zlmacd > 0 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * cross() is either direction; a positive histogram after a cross means it crossed upward, a
      non-positive one downward (the 'blue' / 'red' colour test). The two entries cannot meet on one
      bar. There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code.
      FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, zero-lag MACD crossings on the far side of zero.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_452365_zero_lag_macd_cross_beyond_zero_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 21],
    "signal_len": [9, 5],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal_len": 9}


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


def _zl(x, n):
    e1 = x.ewm(span=n, adjust=False).mean()
    return 2 * e1 - e1.ewm(span=n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    zm = _zl(c, int(p["fast"])) - _zl(c, int(p["slow"]))
    sig = _zl(zm, int(p["signal_len"]))
    hist = zm - sig
    d = zm - sig
    crossed = ((d > 0) & (d.shift(1) <= 0)) | ((d < 0) & (d.shift(1) >= 0))
    le = crossed & (hist > 0) & (zm < 0)
    se = crossed & (hist <= 0) & (zm > 0)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
