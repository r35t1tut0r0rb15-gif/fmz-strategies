"""One-sigma band breakouts (shark792), broker days: the close crossing above the SMA 20 + 1 sd goes long, crossing below
the SMA 20 - 1 sd goes short; the close crossing back through the SMA 20 closes the position.
Port of FMZ strategy #432093 "MCL-YG波动率突破交易策略MCL-YG-Bollinger-Band-Breakout-Pair-Trading-Strategy" (MCL-YG Pair Trading Strategy).

FMZ source id: 432093

Source
    https://www.fmz.com/strategy/432093 (PineScript v5, FMZ last modified 2023-11-14 13:49:12).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 127-186), SMA 20, stdev 20, offsets 1 / 1, ATR risk sizing
    crossover(close, sma + 1 sd) -> entry long;  crossunder(close, sma - 1 sd) -> entry short
    crossunder(close, sma) -> close long;  crossover(close, sma) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A single-instrument strategy (MCL / YG only in the title). The closes are written after the
      entries; a close acts on the position held at the bar's start and does not undo a reversal.
      stdev is the population deviation. The ATR risk quantity is sizing. strategy.entry reverses:
      REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger-style bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the ATR risk-per-trade quantity stored in original_sizing.txt.
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

NAME = "fmz_432093_one_sigma_band_breakout"
FAMILY = "bollinger_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "offset": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "offset": 1.0}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    sma, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    ub, lb = sma + sd * p["offset"], sma - sd * p["offset"]

    def xo(a, b):
        return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    el, es = xo(c, ub), xo(lb, c)
    xl, xs = xo(sma, c), xo(c, sma)
    m = len(el)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if el[i]:
            pos = 1
        if es[i]:
            pos = -1
        if xl[i] and start == 1 and pos == 1:
            pos = 0
        if xs[i] and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
