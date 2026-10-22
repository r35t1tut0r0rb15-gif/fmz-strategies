"""Stacked EMA 9 / 21 / 50 / 200 states, daily bars: the EMAs stacked up hold long, stacked down hold short, each with a 2 % stop from the fill; reversing.
Port of FMZ strategy #472936 "Multi EMA Trend Momentum Recognition and Stop Loss Trading System" (4 EMA Strategy with Stop Loss).

FMZ source id: 472936

Source
    https://www.fmz.com/strategy/472936 (PineScript v5, FMZ last modified 2024-11-25 11:09:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-135), EMA 9 / 21 / 50 / 200; stop 2 % of the average price (sent with the repeated entry calls)
    ema9 > ema21 > ema50 > ema200 -> entry Buy + exit(stop = avg x 0.98);  the mirror -> entry Sell + exit(stop = avg x 1.02)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop uses strategy.position_avg_price, na on the flat signal bar; the stacked state repeats on
      the next bars and arms it from the fill, so it is ported active from the fill bar (#440797) as the
      fixed fraction 0.02 of the fill. Repeated entries while held do nothing. REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code.
      FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fill-price stop as a fixed fraction.
    2 generic: PASS, stacked EMA states with a percent stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_472936_four_ema_stack_state_2pct_stop_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.02, 0.05],
}
DEFAULT_PARAMS = {"sl_pct": 0.02}


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
    e1, e2, e3, e4 = (c.ewm(span=n, adjust=False).mean() for n in (9, 21, 50, 200))
    le = (e1 > e2) & (e2 > e3) & (e3 > e4)
    se = (e1 < e2) & (e2 < e3) & (e3 < e4)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
