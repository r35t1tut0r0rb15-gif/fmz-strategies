"""SMA 21 / 49 cross-ups from flat, daily bars, long only (the default "Strategy 1"). Its 7 % take-profit limit, re-sent every bar from that bar's close, is not ported (pending), so the port has no exit.
Port of FMZ strategy #473350 "双均线趋势跟踪与ATR风控自适应交易策略-Dual-Moving-Average-Trend-Following-Strategy-with-ATR-Based-Risk-Management-System" (Dual Strategy Selector V2 - Cryptogyani).

FMZ source id: 473350

Source
    https://www.fmz.com/strategy/473350 (PineScript v5, FMZ last modified 2024-11-29 14:56:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-195), Strategy 1: SMA 21 / 49, take profit 7 % (Percentage mode), trailing off; 100 % of equity
    crossover(fastMA, slowMA) and strategy.opentrades.size(strategy.opentrades - 1) == 0 -> entry Long Entry;  long: exit(limit = close x 1.07) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default selector is "Strategy 1"; "Strategy 2" (an HTF trend filter, an ATR stop and a 50 %
      qty_percent partial exit) is a separate setting, not ported. The entry gate reads the size of the
      last open trade; it is read as "flat" (the author's evident intent): with no open trade the call
      indexes trade -1, which this reading takes as passing (ambiguity below). The take-profit limit is
      re-sent on every bar from that bar's close, so the level moves after entry: stops() cannot express
      a level re-set every bar, so it is kept pending (as #438034, mark trailing_stop_pending), and the
      port has no exit. Long only. The equity share is not ported. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA cross-ups; per-bar limit described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473350_sma21_49_cross_long_tp_pending"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [21, 10],
    "slow": [49, 100],
}
DEFAULT_PARAMS = {"fast": 21, "slow": 49}


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
    a, b = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
