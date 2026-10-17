"""Bars touching SMA 50 from the other side in an SMA 50 / 100 / 200 stack, closed when the low (high) crosses SMA 20,
1-hour bars: a bar whose high reaches SMA 50 after the prior low was below it, with SMA 50 > SMA 100 > SMA 200, goes
long; the mirror goes short; a long closes when the low crosses under SMA 20, a short when the high crosses over it.
Port of FMZ strategy #483122 "多层移动平均线交叉精确时序趋势跟踪策略-Multi-Layer-Moving-Average-Cross-Precise-Timing-Trend-Following-Strategy" (Multi-SMA Strategy - Core Signals).

FMZ source id: 483122

Source
    https://www.fmz.com/strategy/483122 (PineScript v5, FMZ last modified 2025-02-21 14:32:49).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 98-133), SMA 20 / 50 / 100 / 200, tick-precise crosses on
    golden = high >= sma50 and low[1] < sma50[1] (off: crossover(sma20, sma50)); death mirrored
    long = golden and sma50 > sma100 > sma200; short = death and sma50 < sma100 < sma200
    exitLong = crossunder(low, sma20); exitShort = crossover(high, sma20)
    order: entry long, entry short, close long, close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries reverse (REVERSAL INTENDED). The closes are written after the entries: they act on the position held at
      the bar's start and never undo an entry on that bar (as #430850): a state machine on target positions, exits
      emitted only on going flat.
    * A long and a short entry on one bar: the later (short) wins, as in Pine.
    * The tick-precise switch is a GRID variant. No stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
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

NAME = "fmz_483122_sma50_touch_sma_stack_sma20_exit"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "use_tick_cross": [True, False],
    "fast": [20, 10],
}
DEFAULT_PARAMS = {"fast": 20, "medium": 50, "use_tick_cross": True}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    s20 = c.rolling(int(p["fast"])).mean()
    s50 = c.rolling(int(p["medium"])).mean()
    s100, s200 = c.rolling(100).mean(), c.rolling(200).mean()
    if p["use_tick_cross"]:
        golden = (h >= s50) & (lo.shift(1) < s50.shift(1))
        death = (lo <= s50) & (h.shift(1) > s50.shift(1))
    else:
        golden = (s20 > s50) & (s20.shift(1) <= s50.shift(1))
        death = (s20 < s50) & (s20.shift(1) >= s50.shift(1))
    long_c = (golden & (s50 > s100) & (s100 > s200)).to_numpy()
    short_c = (death & (s50 < s100) & (s100 < s200)).to_numpy()
    x_long = ((lo < s20) & (lo.shift(1) >= s20.shift(1))).to_numpy()
    x_short = ((h > s20) & (h.shift(1) <= s20.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if long_c[i]:
            pos = 1
        if short_c[i]:
            pos = -1
        if x_long[i] and start == 1 and pos == 1:
            pos = 0
        if x_short[i] and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
