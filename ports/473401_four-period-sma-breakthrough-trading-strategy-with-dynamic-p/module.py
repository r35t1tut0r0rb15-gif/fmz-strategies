"""Close crossings of the SMA 4, 2-day bars: the cross up goes long, the cross down goes short; reversing. Each position has a 1 % stop and a 2 % target from its fill price.
Port of FMZ strategy #473401 "Four Period SMA Breakthrough Trading Strategy with Dynamic Profit Loss Management System" (4SMA Strategy with Targets and Stop Loss).

FMZ source id: 473401

Source
    https://www.fmz.com/strategy/473401 (PineScript v5, FMZ last modified 2024-11-29 16:44:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 84-126), SMA 4; target 2 %, stop 1 % of avg
    crossover(close, sma4) -> entry Long;  crossunder -> entry Short;  long: exit(limit = avg x 1.02, stop = avg x 0.99);  short: exit(limit = avg x 0.98, stop = avg x 1.01)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent while the side is held from strategy.position_avg_price, the fill price:
      fixed fractions of the fill, active from the fill (as #440797). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 2-day bars: mark coarse_bar_stop. No sizing code. FREQ =
      "2D" from the backtest header (blocks of 2 broker days, as #429148).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the average-price bracket as fixed fractions.
    2 generic: PASS, SMA 4 crossings with a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_473401_close_cross_sma4_avg_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sma_len": [4, 10],
    "tp_pct": [0.02, 0.04],
    "sl_pct": [0.01, 0.02],
}
DEFAULT_PARAMS = {"sma_len": 4, "tp_pct": 0.02, "sl_pct": 0.01, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s = c.rolling(int(p["sma_len"])).mean()
    le = (c > s) & (c.shift(1) <= s.shift(1))
    se = (c < s) & (c.shift(1) >= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
