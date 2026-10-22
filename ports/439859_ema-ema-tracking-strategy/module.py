"""EMA 50 band breaks, long only, broker days: a close more than 0.3 % above the EMA 50 goes long; a close more than 0.3 % below it closes.
Port of FMZ strategy #439859 "利用EMA指标进行跟踪的趋势策略EMA-Tracking-Strategy" (PingEMA50V.3 Piw).

FMZ source id: 439859

Source
    https://www.fmz.com/strategy/439859 (PineScript v3, FMZ last modified 2024-01-24 14:27:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-142), EMA 50 of close; band 0.003 (a fraction, labelled %)
    upper = ema50 x (1 + 0.003);  lower = ema50 x (1 - 0.003);  close > upper -> entry long;  close < lower -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The band input is used as a fraction (0.3 %), as written. The two tests cannot share a bar. Long
      only. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA band sides.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439859_ema50_band_break_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_period": [50, 20],
    "percent": [0.003, 0.01],
}
DEFAULT_PARAMS = {"ema_period": 50, "percent": 0.003}


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
    e = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    k = float(p["percent"])
    false = pd.Series(False, index=c.index)
    return c > e * (1 + k), c < e * (1 - k), false, false.copy()


def portfolio_kwargs(**params):
    return {}
