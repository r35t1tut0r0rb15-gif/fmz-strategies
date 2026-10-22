"""EMA 9 / 21 crossings, daily bars: the cross up goes long, the cross down goes short; reversing. Each position has a 5 % stop and a 10 % target from its fill price.
Port of FMZ strategy #474051 "Dynamic Dual Moving Average Breakthrough Trading System Dynamic Dual Moving Average Breakthrough Trading System" (EMA Cross Strategy).

FMZ source id: 474051

Source
    https://www.fmz.com/strategy/474051 (PineScript v5, FMZ last modified 2024-12-05 16:22:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-157), EMA 9 / 21 (inputs); stop 5 %, target 10 % of avg; labels on; 100 % of equity
    crossover -> (short: close short) entry Long;  crossunder -> (long: close long) entry Short;  long: exit(stop = avg x 0.95, limit = avg x 1.10);  short: exit(stop = avg x 1.05, limit = avg x 0.90)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent while the side is held from strategy.position_avg_price, the fill price:
      fixed fractions of the fill, active from the fill (as #440797). The closes before each entry only
      repeat the reversal. Labels only. Same rules as #473396 (the EMA lengths are inputs here; rule 7). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on daily bars: mark coarse_bar_stop. The equity share is not ported. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the average-price bracket as fixed fractions.
    2 generic: PASS, EMA crossings with a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND473396 (2 members, best partner #473396, Jaccard 0.708); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_474051_ema9_21_cross_avg_bracket_5_10_reversal_inputs"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.05, 0.03],
    "tp_pct": [0.10, 0.06],
}
DEFAULT_PARAMS = {"sl_pct": 0.05, "tp_pct": 0.10}


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
    c = bars_df["close"]
    a, b = c.ewm(span=9, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
