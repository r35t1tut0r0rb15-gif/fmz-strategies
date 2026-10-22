"""Swing trailing-level (TSL) crossings, broker days: the level is the 3-bar low after the last close above the previous 3-bar high and the 3-bar high after the last close below the previous 3-bar low; the close crossing up through it goes long, crossing down goes short; reversing.
Port of FMZ strategy #485123 "多重摆动指标交易系统基于TSL自动化多方向仓位管理策略-Multi-Directional-Oscillator-Trading-System-TSL-Based-Automated-Position-Management-Strategy" (Accurate Swing Trading System with Auto Entry (Long & Short)).

FMZ source id: 485123

Source
    https://www.fmz.com/strategy/485123 (PineScript v5, FMZ last modified 2025-03-06 10:57:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 226-284), swing 3; quantity 1
    avd = close > highest(high, 3)[1] ? 1 : close < lowest(low, 3)[1] ? -1 : 0;  avn = valuewhen(avd != 0, avd, 0);  tsl = avn == 1 ? lowest(low, 3) : highest(high, 3)
    crossover(close, tsl) -> entry Long, close Short;  crossunder(close, tsl) -> entry Short, close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each crossing closes the other side and enters: REVERSAL INTENDED. The colours, alerts and entry
      lines are drawing only. The quantity 1 is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, swing trailing-level crossings.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: quantity 1 stored, not ported.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_485123_swing3_tsl_cross_reversal"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "swing": [3, 5, 10],
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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["swing"])
    res, sup = h.rolling(n).max(), lo.rolling(n).min()
    up = (c > res.shift(1)).to_numpy()
    dn = (c < sup.shift(1)).to_numpy()
    rv, sv = res.to_numpy(dtype=float), sup.to_numpy(dtype=float)
    m = len(up)
    tsl = np.full(m, np.nan)
    avn = np.nan
    for i in range(m):
        if up[i]:
            avn = 1
        elif dn[i]:
            avn = -1
        tsl[i] = sv[i] if avn == 1 else rv[i]
    t = pd.Series(tsl, index=c.index)
    le = (c > t) & (c.shift(1) <= t.shift(1))
    se = (c < t) & (c.shift(1) >= t.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
