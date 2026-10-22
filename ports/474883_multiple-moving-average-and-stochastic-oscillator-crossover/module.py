"""Triple crossing confirmations, daily bars: SMA 10 crossing over SMA 5 and SMA 6 on a bar where the stochastic %K (15) crosses over its SMA 9 goes long; SMA 5 crossing under SMA 10 and SMA 6 with %D crossing under %K goes short (the short wins a bar with both); reversing.
Port of FMZ strategy #474883 "Multiple Moving Average and Stochastic Oscillator Crossover Quantitative Strategy" (Moving Average and Stochastic Crossover Strategy).

FMZ source id: 474883

Source
    https://www.fmz.com/strategy/474883 (PineScript v5, FMZ last modified 2024-12-12 17:23:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-130), SMA 3 / 5 / 6 / 10 / 80; stochastic 15, D = SMA 9 (constants)
    crossover(ma10, ma5) and crossover(ma10, ma6) and crossover(k, d) -> entry Buy;  crossunder(ma5, ma10) and crossunder(ma5, ma6) and crossunder(d, k) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the sell test repeats two of the buy's crossings (ma5 under ma10 is ma10 over ma5, d
      under k is k over d), so both can hold on one bar; the later call, the short, wins (#437773).
      There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stacked MA / stochastic crossings, as written.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474883_ma10_over_ma5_ma6_stoch_cross_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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


def _x(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    m5, m6, m10 = c.rolling(5).mean(), c.rolling(6).mean(), c.rolling(10).mean()
    k = 100 * (c - lo.rolling(15).min()) / (h.rolling(15).max() - lo.rolling(15).min())
    d = k.rolling(9).mean()
    buy = _x(m10, m5) & _x(m10, m6) & _x(k, d)
    sell = _x(m10, m5) & _x(m6, m5) & _x(k, d)    # crossunder(ma5, ma10), crossunder(ma5, ma6), crossunder(d, k)
    false = pd.Series(False, index=bars_df.index)
    return buy & ~sell, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
