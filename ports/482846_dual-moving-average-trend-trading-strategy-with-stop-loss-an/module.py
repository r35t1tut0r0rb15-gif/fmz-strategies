"""SMA 9 / 21 crossings, broker days, long only: the golden cross goes long with a 1 % stop and a 1 % target from the fill; the death cross closes.
Port of FMZ strategy #482846 "Dual Moving Average Trend Trading Strategy with Stop Loss and Take Profit" (Moving Average Crossover with Stop Loss and Take Profit).

FMZ source id: 482846

Source
    https://www.fmz.com/strategy/482846 (PineScript v6, FMZ last modified 2025-02-27 17:36:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-119), SMA 9 / 21; stop 1 %; target 1 %
    crossover(sma9, sma21) -> entry Long + exit(stop = avg x 0.99, limit = avg x 1.01);  crossunder(sma9, sma21) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is sent on the flat signal bar, where position_avg_price is still na; it is ported as the
      1 % / 1 % bracket around the fill, active from the fill bar (as #440797). A golden cross cannot
      repeat while long (the death cross between closes it). Long only; Opposite entries cannot occur.
      Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, SMA crossings with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482846_sma9_21_cross_1pct_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_loss_percent": [1.0, 2.0],
    "take_profit_percent": [1.0, 2.0],
}
DEFAULT_PARAMS = {"stop_loss_percent": 1.0, "take_profit_percent": 1.0, "short_length": 9, "long_length": 21}


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
    f = c.rolling(int(p["short_length"])).mean()
    s = c.rolling(int(p["long_length"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    lx = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    sl = pd.Series(float(p["stop_loss_percent"]) / 100, index=idx).shift(1)
    tp = pd.Series(float(p["take_profit_percent"]) / 100, index=idx).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
