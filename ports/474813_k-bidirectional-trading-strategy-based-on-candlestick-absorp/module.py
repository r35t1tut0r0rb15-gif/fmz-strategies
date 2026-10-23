"""Broker days: two opposite-coloured candles where the second has the larger body and the lowest volume of the three bars goes long on a green second candle and short on a red one; the opposite signal reverses.
Port of FMZ strategy #474813 "基于K线蜡烛图吸收形态的双向交易量化策略-Bidirectional-Trading-Strategy-Based-on-Candlestick-Absorption-Pattern-Analysis" (Candle Absorption Strategy).

FMZ source id: 474813

Source
    https://www.fmz.com/strategy/474813 (PineScript v5, FMZ last modified 2024-12-12 11:27:27).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 96-154), opposite candles; |body| growing; volume[1] > volume < volume[2]; 100 % of equity
    all_conditions = opposite colours and abs(close[1] - open[1]) < abs(close - open) and volume[1] > volume and volume < volume[2]
    buySignal = all_conditions and close > open and not isLong -> entry Long;  sellSignal = all_conditions and close < open and not isShort -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The isLong / isShort flags are reset on every bar the strategy is flat at the close, which
      includes the signal bar itself (the fill comes at the next open), so they only stop a repeat of
      the side already held, which adds nothing anyway: the entries are the absorption candles. Entries
      only; an opposite entry reverses. REVERSAL INTENDED. 100 % of equity is sizing. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, absorption candles on falling volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) compared over three bars; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474813_candle_absorption_low_volume_reversal"
FAMILY = "candlestick_pattern"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "body_ratio": [1.0, 1.5],
}
DEFAULT_PARAMS = {"body_ratio": 1.0}


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
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    o1, c1 = o.shift(1), c.shift(1)
    opp = ((c1 > o1) & (c < o)) | ((c1 < o1) & (c > o))
    bigger = (c1 - o1).abs() * float(p["body_ratio"]) < (c - o).abs()
    vol_dip = (v.shift(1) > v) & (v < v.shift(2))
    allc = opp & bigger & vol_dip
    buy = allc & (c > o)
    sell = allc & (c < o)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
