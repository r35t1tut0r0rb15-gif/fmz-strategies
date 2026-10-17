"""MACD 12 / 26 / 9 crosses, always in, broker days: the MACD line crossing above its signal goes long, crossing
below goes short (the source's feature-distance test is OR-ed with the bare cross, so the cross alone decides).
Port of FMZ strategy #490794 "技术指标距离测量与MACD反转混合量化交易策略-Technical-Indicator-Distance-Measurement-and-MACD-Reversal-Hybrid-Quantitative-Trading-Strategy" (Bysq-Distance Reversal Entry - BTCUSDT (v6)).

FMZ source id: 490794

Source
    https://www.fmz.com/strategy/490794 (PineScript v6, FMZ last modified 2025-04-16 15:19:46).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 155-224), MACD 12 / 26 / 9
    buy = (distance to the bullish centroid < to the bearish one and crossover(macd, signal)) or crossover(macd, signal)
    sell = the mirror;  buy -> close "Sell", entry long;  sell -> close "Buy", entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The distance branch implies the bare cross, so buy == crossover(macd, signal) and sell == crossunder: the
      feature vector does not change any signal and is not computed.
    * The closes come before the entries on the same bar: a stop-and-reverse (REVERSAL INTENDED).
    * The open / closed trade profit lookups only feed the display.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_490794_macd_cross_always_in"
FAMILY = "macd_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 34],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    up = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).astype(bool)
    dn = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
