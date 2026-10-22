"""EMA 10 / 20 crossings on the side of the EMA 50, broker days: the confirmed up-cross goes long, the confirmed down-cross goes short; a close back through the EMA 10 closes the side of the last signal; reversing.
Port of FMZ strategy #491892 "EMA双重交叉动态止损量化策略-EMA-Dual-Crossover-Dynamic-Stop-Loss-Quantitative-Strategy" (EMA Crossover Strategy).

FMZ source id: 491892

Source
    https://www.fmz.com/strategy/491892 (PineScript v5, FMZ last modified 2025-04-24 16:59:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-182), EMA 10 / 20 / 50; 100 % of equity
    crossover(ema10, ema20) and close > ema50 -> bullish state, entry Long;  crossunder and close < ema50 -> bearish state, entry Short
    bullish state and close < ema10 -> close Long;  bearish state and close > ema10 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bullish / bearish state is kept until the other signal, so the EMA 10 close repeats harmlessly
      while flat; a close on the entry's own bar does not cancel that entry. An entry on the other side
      reverses (REVERSAL INTENDED). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with a trend filter and an EMA exit.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
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

NAME = "fmz_491892_ema10_20_cross_ema50_side_ema10_exit_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length10": [10, 5],
    "length20": [20, 30],
}
DEFAULT_PARAMS = {"length10": 10, "length20": 20, "length50": 50}


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

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    a, b, e50 = ema(p["length10"]), ema(p["length20"]), ema(p["length50"])
    bull = ((a > b) & (a.shift(1) <= b.shift(1)) & (c > e50)).to_numpy()
    bear = ((a < b) & (a.shift(1) >= b.shift(1)) & (c < e50)).to_numpy()
    below, above = (c < a).to_numpy(), (c > a).to_numpy()
    m = len(c)
    lx, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    state = 0
    for i in range(m):
        if bull[i]:
            state = 1
        if bear[i]:
            state = -1
        lx[i] = state == 1 and below[i]
        sx[i] = state == -1 and above[i]
    le, se = pd.Series(bull, index=c.index), pd.Series(bear, index=c.index)
    return le, pd.Series(lx, index=c.index) & ~le & ~se, se, pd.Series(sx, index=c.index) & ~se & ~le


def portfolio_kwargs(**params):
    return {}
