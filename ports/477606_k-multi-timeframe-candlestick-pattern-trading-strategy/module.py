"""Outside engulfing candles, broker days: a green candle closing above the previous high after opening below the previous low (the previous candle red) goes long, the mirror goes short; reversing.
Port of FMZ strategy #477606 "多周期日线K线形态信号交易策略-Multi-Timeframe-Candlestick-Pattern-Trading-Strategy" (Sensex Option Buy/Sell Signals).

FMZ source id: 477606

Source
    https://www.fmz.com/strategy/477606 (PineScript v5, FMZ last modified 2025-01-06 16:40:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-137), engulfing tests on the prior high / low; doji labels only; timeframe input unused
    close[1] < open[1] and close > open and close > high[1] and open < low[1] -> entry Buy;  close[1] > open[1] and close < open and close < low[1] and open > high[1] -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The engulfing tests use the previous candle's high and low, as written. The doji test and the
      timeframe input only draw. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, outside engulfing candles.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477606_outside_engulfing_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    top, bot = h.shift(1), lo.shift(1)
    le = (c.shift(1) < o.shift(1)) & (c > o) & (c > top) & (o < bot)
    se = (c.shift(1) > o.shift(1)) & (c < o) & (c < bot) & (o > top)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
