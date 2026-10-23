"""Broker days: the EMA 9 crossing over the EMA 21 on volume above its 20-day average goes long, crossing under on such volume goes short; the opposite signal reverses.
Port of FMZ strategy #473137 "Multi Period Moving Average Crossover with Volume Analysis System" (Cruzamento de Medias com Volume).

FMZ source id: 473137

Source
    https://www.fmz.com/strategy/473137 (PineScript v5, FMZ last modified 2024-11-27 15:08:39).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 98-155), MA type EMA / EMA (SMA / WMA options); lengths 9 / 21; volume SMA 20; EMA 200 plotted only
    longCondition = crossover(ma1, ma2) and volume > volSMA -> entry Compra;  shortCondition = crossunder(ma1, ma2) and volume > volSMA -> entry Venda

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries only; an opposite entry reverses. The default MA type (EMA for both) is ported; the SMA /
      WMA options are not. The EMA 200 only plots. REVERSAL INTENDED. No sizing code. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA 9 / 21 crossings on above-average volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473137_ema9_21_cross_volume_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 12],
    "slow": [21, 26],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "vol_len": 20}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    vol_ok = v > v.rolling(int(p["vol_len"])).mean()
    buy = (f > s) & (f.shift(1) <= s.shift(1)) & vol_ok
    sell = (f < s) & (f.shift(1) >= s.shift(1)) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
