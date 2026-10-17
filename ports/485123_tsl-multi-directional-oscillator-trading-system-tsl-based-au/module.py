"""Swing trailing-line crosses, always in, broker days: a close above the previous 3-bar high sets the trend up (below the
previous 3-bar low sets it down); the trailing line is the 3-bar low in an up-trend and the 3-bar high otherwise; the
close crossing above the line goes long, crossing below goes short.
Port of FMZ strategy #485123 "多重摆动指标交易系统基于TSL自动化多方向仓位管理策略-Multi-Directional-Oscillator-Trading-System-TSL-Based-Automated-Position-Management-Strategy" (Accurate Swing Trading System with Auto Entry (Long & Short)).

FMZ source id: 485123

Source
    https://www.fmz.com/strategy/485123 (PineScript v5, FMZ last modified 2025-03-06 10:57:03).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 230-280), swing 3
    res = highest(high, 3); sup = lowest(low, 3); avd = close > res[1] ? 1 : close < sup[1] ? -1 : 0
    avn = valuewhen(avd != 0, avd, 0); tsl = avn == 1 ? sup : res
    crossover(close, tsl) -> entry long, close short;  crossunder(close, tsl) -> entry short, close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * avn is na until the first non-zero avd; then tsl is the 3-bar high (as written).
    * The close after each entry is the reversal itself (REVERSAL INTENDED); the two crosses cannot fall on one bar.
      The open-trade price tracking only feeds labels.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rolling extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the qty 1 quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_485123_swing_tsl_cross"
FAMILY = "swing_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "swing": [3, 5],
}
DEFAULT_PARAMS = {"swing": 3}


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
    n = int(p["swing"])
    c = bars_df["close"]
    res, sup = bars_df["high"].rolling(n).max(), bars_df["low"].rolling(n).min()
    avd = np.where(c > res.shift(1), 1, np.where(c < sup.shift(1), -1, 0))
    avn = pd.Series(np.where(avd != 0, avd, np.nan), index=c.index)
    last = np.full(len(c), np.nan)
    cur = np.nan
    for i, v in enumerate(avn.to_numpy()):
        if not np.isnan(v):
            cur = v
        last[i] = cur
    tsl = pd.Series(np.where(last == 1, sup.to_numpy(), res.to_numpy()), index=c.index)
    long_e = ((c > tsl) & (c.shift(1) <= tsl.shift(1))).astype(bool)
    short_e = ((c < tsl) & (c.shift(1) >= tsl.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
