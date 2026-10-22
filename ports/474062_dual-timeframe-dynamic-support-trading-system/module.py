"""Daily and weekly support bands, daily bars, long only: EMA 51 crossing over SMA 50 with the EMA 51 over the weekly EMA 21 buys, unless a sell fires on the same bar; EMA 51 crossing under SMA 50 above the weekly EMA 21, or the weekly EMA 21 crossing under the weekly SMA 20, sells.
Port of FMZ strategy #474062 "Dual Timeframe Dynamic Support Trading System" (Demo GPT - Bull Market Support Band).

FMZ source id: 474062

Source
    https://www.fmz.com/strategy/474062 (PineScript v5, FMZ last modified 2024-12-05 16:44:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-162), long band: SMA 20 / EMA 21 on "W"; short band: SMA 50 / EMA 51 on "D"; 100 % of equity, commission 0.1 %, slippage 3
    crossunder(emaD, smaD) and emaD > emaW -> close_all;  crossunder(emaW, smaW) -> close_all;  crossover(emaD, smaD) and emaD > emaW and no close signal -> entry Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The weekly request (no lookahead) is the last completed broker week (as #437508): the SMA 20 and
      EMA 21 of weekly closes of the previous broker week, stepped on the daily bars; "D" is the chart.
      The date window is always true. Long only. The costs and the equity share are not ported. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; completed weekly values.
    2 generic: PASS, daily band crossings filtered by the weekly band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size, commission and slippage stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474062_daily_band_cross_weekly_band_filter_long"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_sma": [50, 100],
    "long_sma": [20, 40],
}
DEFAULT_PARAMS = {"short_sma": 50, "long_sma": 20}


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


def _x(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")   # the Monday of the broker week
    wk = c.groupby(week).last()
    nl = int(p["long_sma"])
    w_sma = pd.Series(wk.rolling(nl).mean().shift(1).reindex(week).to_numpy(), index=c.index)
    w_ema = pd.Series(wk.ewm(span=nl + 1, adjust=False).mean().shift(1).reindex(week).to_numpy(), index=c.index)
    ns = int(p["short_sma"])
    d_sma = c.rolling(ns).mean()
    d_ema = c.ewm(span=ns + 1, adjust=False).mean()
    out = (_x(d_sma, d_ema) & (d_ema > w_ema)) | _x(w_sma, w_ema)
    le = _x(d_ema, d_sma) & (d_ema > w_ema) & ~out
    false = pd.Series(False, index=bars_df.index)
    return le, out, false, false.copy()


def portfolio_kwargs(**params):
    return {}
