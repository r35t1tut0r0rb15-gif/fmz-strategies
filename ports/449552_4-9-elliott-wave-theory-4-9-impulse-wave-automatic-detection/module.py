"""Three rising (falling) closes with the close above (below) the close 9 bars back, daily bars, with a stop at the signal bar's low (high): such a bar goes long unless already long, the mirror goes short
unless already short; reversing.
Port of FMZ strategy #449552 "艾略特波浪理论4-9脉冲波自动检测交易策略-Elliott-Wave-Theory-4-9-Impulse-Wave-Automatic-Detection-Trading-Strategy" (LW: 4-9 indicator).

FMZ source id: 449552

Source
    https://www.fmz.com/strategy/449552 (PineScript v5, FMZ last modified 2024-04-26 17:32:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-152), consecutive closes 3; days ago 9; stop low / high of the signal bar
    long = 3 rising closes and close > close[9] -> (position <= 0) entry Long, exit(stop = low);  short mirrored -> (position >= 0) entry Short, exit(stop = high)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is set on the signal bar at its low (high): sl_stop = (close - low) / close for longs
      and (high - close) / close for shorts, shifted one bar inside stops() and re-based on the fill.
      Entries are taken only when not already on that side, so the stop is never re-sent inside a
      trade. Daily stop module: mark coarse_bar_stop. strategy.entry reverses: REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed on the signal bar.
    2 generic: PASS, consecutive closes with a 9-bar momentum filter, signal-bar stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_449552_three_closes_9bar_momentum_bar_stop_reversal"
FAMILY = "momentum_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "consclos": [3, 4],
    "daysago": [9, 13],
}
DEFAULT_PARAMS = {"consclos": 3, "daysago": 9}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    k = int(p["consclos"])
    rise = pd.Series(True, index=c.index)
    fall = pd.Series(True, index=c.index)
    for i in range(1, k + 1):
        rise &= c.shift(i - 1) > c.shift(i)
        fall &= c.shift(i - 1) < c.shift(i)
    d = int(p["daysago"])
    le = rise & (c > c.shift(d))
    se = fall & (c < c.shift(d))
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    c = bars_df["close"]
    sl = ((c - bars_df["low"]) / c).where(le, ((bars_df["high"] - c) / c).where(se))
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
