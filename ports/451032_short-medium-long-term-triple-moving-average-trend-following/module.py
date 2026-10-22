"""Closes under the 3-bar average of lows in an uptrend buy, daily bars, long only: a close under the SMA 3 of lows and above the SMA 30 goes long; a close above the SMA 3 of highs closes.
Port of FMZ strategy #451032 "Short Medium Long Term Triple Moving Average Trend Following Strategy" (MM3 (Estratégia de Médias Móveis - Entrada/Saída Simples)).

FMZ source id: 451032

Source
    https://www.fmz.com/strategy/451032 (PineScript v5, FMZ last modified 2024-05-11 12:04:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-126), SMA 3 of lows / highs; SMA 30 of closes; dates (computed, unused)
    close < sma(low, 3) and close > sma(close, 30) -> entry Buy;  close > sma(high, 3) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The date inputs are converted but never tested. A repeated entry while long is ignored; the
      entry and the close cannot meet on one bar. Long only. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, dips under the low average in an uptrend, high-average exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_451032_close_under_low_avg3_above_sma30_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [3, 5],
    "trend_len": [30, 50],
}
DEFAULT_PARAMS = {"short_len": 3, "trend_len": 30}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["short_len"])
    le = (c < lo.rolling(k).mean()) & (c > c.rolling(int(p["trend_len"])).mean())
    lx = c > h.rolling(k).mean()
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
