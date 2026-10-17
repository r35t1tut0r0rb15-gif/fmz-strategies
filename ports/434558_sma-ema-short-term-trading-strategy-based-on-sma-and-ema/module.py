"""EMA 21 / SMA 20 crosses with close-sized exits, broker days: the EMA crossing above the SMA goes long, the SMA crossing
above the EMA goes short (reversing); each trade carries a 1 % stop and a 2 % target.
Port of FMZ strategy #434558 "基于SMA和EMA指标的短线交易策略Short-term-Trading-Strategy-Based-on-SMA-and-EMA" (Cruce de SMA y EMA - Estrategia).

FMZ source id: 434558

Source
    https://www.fmz.com/strategy/434558 (PineScript v5, FMZ last modified 2023-12-07 15:29:12).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 153-177), SMA 20, EMA 21; stop 1 %, target 2 % of the latest close
    crossover(ema21, sma20) -> entry long;  crossover(sma20, ema21) -> entry short
    exit long (stop = close (1 - 1 %), limit = close (1 + 2 %));  exit short (stop = close (1 + 1 %), limit = close (1 - 2 %))   (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-issued every bar at distances from the latest close, so the levels move with
      the close in both directions after entry: stops() cannot express that (mark
      trailing_stop_pending). The port fixes them as fractions of the fill: sl_stop 0.01, tp_stop
      0.02. Both exits share one id with different entries: read as one exit per entry.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on daily bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-sized exits fixed at entry (approximation stated).
    2 generic: PASS, average crosses and percent exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434558_ema_sma_cross_close_exits"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [21, 10],
    "tp_pct": [0.02, 0.04],
}
DEFAULT_PARAMS = {"sma_len": 20, "ema_len": 21, "sl_pct": 0.01, "tp_pct": 0.02}


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
    s = c.rolling(int(p["sma_len"])).mean()
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    le = ((e > s) & (e.shift(1) <= s.shift(1))).astype(bool)
    se = ((s > e) & (s.shift(1) <= e.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
