"""EMA 9 / 21 crossings, daily bars: the cross up goes long and the cross down goes short, each with a 0.7 % stop and a 0.5 % target from the fill; reversing.
Port of FMZ strategy #454143 "EMA交叉动量短线交易策略-EMA-Crossover-Momentum-Scalping-Strategy" (Scalping Strategy (EMA 9 / 21)).

FMZ source id: 454143

Source
    https://www.fmz.com/strategy/454143 (PineScript v5, FMZ last modified 2024-06-14 15:24:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-138), EMA 9 / 21; stop 0.7 %, target 0.5 % of the average price
    crossover -> entry Long;  crossunder -> entry Short;  long: exit(limit = avg x 1.005), exit(stop = avg x 0.993);  short: exit(limit = avg x 0.995), exit(stop = avg x 1.007)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are sent every bar from the average (fill) price while in a position: ported active
      from the fill bar (#440797) as fixed fractions 0.007 / 0.005 of the fill, on the right side for
      both directions. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day
      bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fill-price bracket as fixed fractions.
    2 generic: PASS, EMA crossings.
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

NAME = "fmz_454143_ema9_21_cross_fill_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.007, 0.02],
    "tp_pct": [0.005, 0.02],
}
DEFAULT_PARAMS = {"sl_pct": 0.007, "tp_pct": 0.005, "fast": 9, "slow": 21}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
