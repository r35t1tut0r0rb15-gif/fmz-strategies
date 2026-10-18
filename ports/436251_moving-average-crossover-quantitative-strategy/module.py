"""EMA filter with a smoothed-price offset, broker days: the close over the EMA 13 with the gap between the EMA 12 of the close and its EMA 9 above a small negative level goes long; the close under it
with that gap below a small positive level goes short (reversing). The "MACD" is the fast EMA alone (the slow one is commented out).
Port of FMZ strategy #436251 "Moving Average Crossover Quantitative Strategy" (LONERTESTV2).

FMZ source id: 436251

Source
    https://www.fmz.com/strategy/436251 (PineScript v5, FMZ last modified 2023-12-22 15:05:24).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 127-153), EMA 13; "MACD" = EMA 12 of the close; signal EMA 9; levels +-5 (price units)
    delta = ema(close, 12) - ema(ema(close, 12), 9);  buy_entry = close > ema13 and delta > 5 ? true : close > ema13 and delta > -5;  sell_entry = close < ema13 and delta < -5 ? true : close < ema13 and delta < 5
    entry long (buy_entry);  entry short (sell_entry)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ternaries reduce to buy = close > EMA and delta > -5, sell = close < EMA and delta < 5. Criterion 2:
      the +-5 levels are price units; the port uses +-level_frac x close (0.000125 reads 5 on BTC near
      40000; 0.001 is wider). The conditions are states re-sent every bar. REVERSAL INTENDED. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit levels -> fractions of the close.
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

NAME = "fmz_436251_ema_filter_smoothed_offset"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "level_frac": [0.000125, 0.001],
    "ema_length": [13, 21],
}
DEFAULT_PARAMS = {"level_frac": 0.000125, "ema_length": 13, "fast": 12, "macd_length": 9}


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
    ema = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean()
    delta = macd - macd.ewm(span=int(p["macd_length"]), adjust=False).mean()
    lv = float(p["level_frac"]) * c
    le = ((c > ema) & (delta > -lv)).fillna(False).astype(bool)
    se = ((c < ema) & (delta < lv)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
