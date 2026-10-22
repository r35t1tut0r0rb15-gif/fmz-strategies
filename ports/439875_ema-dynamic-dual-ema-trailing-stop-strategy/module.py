"""EMA 60 / 90 trend with MACD confirmation, broker days: a close above the EMA 60 above the EMA 90 with the MACD over its signal goes long, the mirror goes short; reversing (the written exits can never fire).
Port of FMZ strategy #439875 "动态双EMA游离停止策略Dynamic-Dual-EMA-Trailing-Stop-Strategy" (Improved EMA & CDC Trailing Stop Strategy).

FMZ source id: 439875

Source
    https://www.fmz.com/strategy/439875 (PineScript v5, FMZ last modified 2024-01-24 15:13:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 103-157), EMA 60 / 90; ATR 24, multiplier 4; profit multiplier 2; MACD 12 / 26 / 9
    long = close > ema60 > ema90 and macd > signal and close > close - 4 atr;  short mirror;  entry Long / entry Short
    close Long when close >= close + 2 atr or close < close - 4 atr;  close Short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop and target lines are built from the same bar's close, so "close >= close + 2 ATR" and
      "close < close - 4 ATR" can never hold and no close is ever sent; positions change only by
      reversal, as written (the intended trailing exit is owed). strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA stack and MACD.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439875_ema60_90_macd_trend_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema60_period": [60, 30],
    "ema90_period": [90, 120],
}
DEFAULT_PARAMS = {"ema60_period": 60, "ema90_period": 90}


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
    a = c.ewm(span=int(p["ema60_period"]), adjust=False).mean()
    b = c.ewm(span=int(p["ema90_period"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    le = (c > a) & (a > b) & (macd > sig)
    se = (c < a) & (a < b) & (macd < sig)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
