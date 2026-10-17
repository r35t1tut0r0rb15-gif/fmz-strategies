"""Closes above the upper Bollinger band (20, 2) go long, closed by a close below the lower band, long only, two-day
bars.
Port of FMZ strategy #482830 "基于布林带动态均值突破的量化交易策略-Dynamic-Bollinger-Bands-Breakout-Quantitative-Trading-Strategy" (Demo GPT - Bollinger Bands).

FMZ source id: 482830

Source
    https://www.fmz.com/strategy/482830 (PineScript v6, FMZ last modified 2025-02-20 14:51:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 124-160), length 20, basis SMA (input: SMA / EMA / RMA / WMA / VWMA),
StdDev 2
    close > basis + 2 stdev -> entry long; close < basis - 2 stdev -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The basis type is an input that only switches the average: SMA (the default) and EMA are GRID variants; the
      VWMA option weights by volume (check 8) and is not offered; RMA and WMA are left out of the 4-trial grid.
    * Every bar above the band is an entry signal (same-side ignored while held); entries and exits cannot fall on
      one bar. Long only. Signal module, no stops. Two-day bars are blocks of broker-day dates from 1970-01-01
      (decision owed, as #426509); FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the 0.1 % commission quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8); the source's VWMA basis option is not offered.
Session open: broker day (17:00 America/New_York, DST by the zone) in two-day blocks; no venue-open rule.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482830_bb_upper_breakout_lower_exit_long_2d"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_type": ["SMA", "EMA"],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "ma_type": "SMA", "mult": 2.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=2):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def _basis(c, n, kind):
    if kind == "SMA":
        return c.rolling(n).mean()
    if kind == "EMA":
        return c.ewm(span=n, adjust=False).mean()
    raise ValueError(f"unsupported ma_type {kind!r}")


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis = _basis(c, n, p["ma_type"])
    dev = p["mult"] * c.rolling(n).std(ddof=0)
    long_e = (c > basis + dev).astype(bool)
    long_x = (c < basis - dev).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
