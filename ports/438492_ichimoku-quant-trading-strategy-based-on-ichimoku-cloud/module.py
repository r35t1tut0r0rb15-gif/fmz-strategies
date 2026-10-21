"""Close crossings of the current Senkou A with the Senkou B side, broker days: the close crossing over span A while above span B goes long, crossing under span A while below span B goes short; reversing.
The trailing exit is never armed.
Port of FMZ strategy #438492 "基于Ichimoku云图的量化交易策略Quant-Trading-Strategy-Based-on-Ichimoku-Cloud" (Ichimoku Cloud Strategy with SL, TP, and Trailing Stop).

FMZ source id: 438492

Source
    https://www.fmz.com/strategy/438492 (PineScript v5, FMZ last modified 2024-01-12 14:20:43).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 136-183), conversion 9, base 26, span B 52, displacement 26 (unused); ATR 14 (stop 2 x, target 4 x: unused)
    long = crossover(close, span A) and close > span B -> entry Buy, close Sell;  short = crossunder(close, span A) and close < span B -> entry Sell, close Buy
    cancel("Trailing Stop") every bar;  on a signal: trailingStopPrice := max(trailingStopPrice, close - 2 ATR) (starts na), exit(trail_offset = 2 ATR, trail_price = trailingStopPrice)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spans are the current (undisplaced) values, as the code compares them. trailingStopPrice
      starts na and math.max / math.min of na stay na, so the trailing exit has no activation price and is
      cancelled on the next bar: no exit is placed. The ATR stop and target variables feed no order. The
      closes of the opposite side and the reversing entries give the same position: REVERSAL INTENDED.
      No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku spans.
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

NAME = "fmz_438492_close_cross_span_a_span_b_side"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion": [9, 7],
    "base": [26, 22],
}
DEFAULT_PARAMS = {"conversion": 9, "base": 26, "span_b": 52}


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


def _donchian(h, lo, n):
    return (lo.rolling(n).min() + h.rolling(n).max()) / 2


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    conv = _donchian(h, lo, int(p["conversion"]))
    base = _donchian(h, lo, int(p["base"]))
    lead1 = (conv + base) / 2
    lead2 = _donchian(h, lo, int(p["span_b"]))
    up = (c > lead1) & (c.shift(1) <= lead1.shift(1)) & (c > lead2)
    dn = (c < lead1) & (c.shift(1) >= lead1.shift(1)) & (c < lead2)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
