"""EMA 3 / 30 crossings on the EMA 50 side, broker days: the EMA 3 crossing over the EMA 30 with the close above the EMA 50 goes long, crossing under with the close below it goes short; reversing (the
written exits name ids no entry has).
Port of FMZ strategy #442233 "移动平均线与MACD结合的RSI指标交易策略A-Combined-RSI-Strategy-with-Moving-Average-and-MACD" (sachin 3.30).

FMZ source id: 442233

Source
    https://www.fmz.com/strategy/442233 (PineScript v5, FMZ last modified 2024-02-20 14:28:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 127-190), EMA 3 / 30 / 50; RSI 14 and MACD for colours only
    crossover(ema3, ema30) and close > ema50 -> entry Buy;  crossunder(ema3, ema30) and close < ema50 -> entry Sell;  exit tests -> strategy.close("BuyExit") / strategy.close("SellExit")

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes name "BuyExit" and "SellExit", ids no entry has, so they never close anything;
      positions end only at the opposite entry. strategy.entry reverses: REVERSAL INTENDED. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings on the EMA 50 side.
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

NAME = "fmz_442233_ema3_30_cross_ema50_side_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema3_length": [3, 9],
    "ema30_length": [30, 50],
}
DEFAULT_PARAMS = {"ema3_length": 3, "ema30_length": 30, "ema50_length": 50}


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
    e3 = c.ewm(span=int(p["ema3_length"]), adjust=False).mean()
    e30 = c.ewm(span=int(p["ema30_length"]), adjust=False).mean()
    e50 = c.ewm(span=int(p["ema50_length"]), adjust=False).mean()
    up = (e3 > e30) & (e3.shift(1) <= e30.shift(1)) & (c > e50)
    dn = (e3 < e30) & (e3.shift(1) >= e30.shift(1)) & (c < e50)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
