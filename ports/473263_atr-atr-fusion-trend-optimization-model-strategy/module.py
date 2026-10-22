"""Buying-pressure ratio crossings, daily bars: a weighted average of 8 / 13 / 21 / 34 / 55-bar buying-pressure ratios (SMA 3) crossing over 58 goes long, crossing under 42 goes short; reversing.
Port of FMZ strategy #473263 "ATR融合趋势优化模型策略-ATR-Fusion-Trend-Optimization-Model-Strategy" (Fibonacci ATR Fusion - Strategy [presentTrading]).

FMZ source id: 473263

Source
    https://www.fmz.com/strategy/473263 (PineScript v5, FMZ last modified 2024-11-28 17:06:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-182), BP = close - min(low, close[1]); ratio = 100 x sum(BP) / sum(true range) over 8 / 13 / 21 / 34 / 55, weights 5..1; SMA 3; levels 58 / 42; 4-step take profit off; 10 % of equity, commission 0.1 %, slippage 1
    crossover(avg, 58) -> entry Long;  crossunder(avg, 42) -> close Long;  crossunder(avg, 42) -> entry Short;  crossover(avg, 58) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each exit test is the opposite entry's test, so the closes only repeat the reversals (#437773).
      The partial take-profits are switched off by default. The costs and the equity share are not
      ported. REVERSAL INTENDED. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, buying-pressure ratio crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size, commission and slippage stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473263_fib_weighted_buying_pressure_ratio_cross_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "long_th": [58, 55],
    "short_th": [42, 45],
}
DEFAULT_PARAMS = {"long_th": 58, "short_th": 42}


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
    c1 = c.shift(1)
    t_low = np.minimum(lo, c1)                   # na on the first bar (math.min with na)
    t_high = np.maximum(h, c1)
    tr = t_high - t_low
    bp = c - t_low

    def ratio(n):
        return 100 * bp.rolling(n).sum() / tr.rolling(n).sum()

    w = (5 * ratio(8) + 4 * ratio(13) + 3 * ratio(21) + 2 * ratio(34) + ratio(55)) / 15
    ws = w.rolling(3).mean()
    lt, st = float(p["long_th"]), float(p["short_th"])
    le = (ws > lt) & (ws.shift(1) <= lt)
    se = (ws < st) & (ws.shift(1) >= st)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
