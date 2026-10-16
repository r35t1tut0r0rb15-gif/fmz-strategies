"""Snap-back long against a falling MA stack, broker days: with SMA 200 > SMA 50 > EMA 34 > SMA 20 > EMA 8 and EMA 8 more
than 2 % below SMA 20, the close crossing back above EMA 8 goes long, with a 4 % stop and a 6 % target.
Port of FMZ strategy #429953 "Snap Back Moving Average Counter trend Strategy".

FMZ source id: 429953

Source
    https://www.fmz.com/strategy/429953 (PineScript v4, FMZ last modified 2023-10-23 15:31:21).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 215-383), EMA 8 / 34, SMA 20 / 50 / 200, gap 2 %, aggressive, trend "Up", stop 4 % / target 6 %
    setup = sma200 > sma50 > ema34 > sma20 > ema8 and |sma20 - ema8| > 2 % of the price; trigger = crossover(close, ema8)
    setup and trigger -> entry long; exit(stop = avg x 0.96, limit = avg x 1.06) while long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Defaults: aggressive entry (0), RunTrend "Up" (long side only), stop criterion SL and profit
      criterion TGT%: a fixed bracket of 4 % / 6 % of the average entry price (the fill): sl_stop 0.04,
      tp_stop 0.06. The MD_EMA / trailing / partial-exit branches are input options (not ported).
    * Long only; Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). Stops on
      1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, moving-average order, a percentage gap and percentage exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the exit options stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_429953_snap_back_ma_stack_long"
FAMILY = "ma_pullback"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "gap": [0.02, 0.01],
    "sl_pct": [4.0, 2.0],
}
DEFAULT_PARAMS = {"gap": 0.02, "sh_ema": 8, "md_ema": 34, "sh_sma": 20, "md_sma": 50, "lg_sma": 200, "sl_pct": 4.0,
                  "tp_pct": 6.0}


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
    e8 = c.ewm(span=int(p["sh_ema"]), adjust=False).mean()
    e34 = c.ewm(span=int(p["md_ema"]), adjust=False).mean()
    s20, s50, s200 = (c.rolling(int(p[k])).mean() for k in ("sh_sma", "md_sma", "lg_sma"))
    stack = (s200 > s50) & (s50 > e34) & (e34 > s20) & (s20 > e8)
    gap = (s20 - e8).abs() > c * p["gap"]
    trig = (c > e8) & (c.shift(1) <= e8.shift(1))
    long_e = (stack & gap & trig).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100, "tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
