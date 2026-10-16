"""Bollinger + Fibonacci, as written (effectively short only): the close crossing under the lower band
(20, 2) while the high is below the 50-bar high goes short; the close crossing back over the middle
band closes it. The long side's filter (low above the 50-bar HIGH) can never hold.
Port of FMZ strategy #427516 "Bollinger Bands and Fibonacci Trading Strategy".

FMZ source id: 427516

Source
    https://www.fmz.com/strategy/427516 (PineScript v5, FMZ last modified 2023-09-21 21:04:38).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 195-258), BB 20 x 2, Fibonacci 0 % / 100 %, 50 bars
    fib_range = highest(high, 50) - lowest(low, 50)
    fib_high = highest(high, 50) - range x 0; fib_low = lowest(low, 50) + range x 1.0 (= the 50-bar high)
    crossover(close, upper) and low > fib_low and not short_flag -> entry long
    crossunder(close, lower) and high < fib_high and not long_flag -> entry short
    crossunder(close, basis) -> close long; crossover(close, basis) -> close short (flags reset)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written, with the default levels (0 % and 100 %) the long filter compares the low with the
      50-bar high (current bar included): never true. The short filter is true unless this bar makes
      the 50-bar high. Ported literally (long side dead; decision owed for other Fibonacci levels).
    * The script's own flags (var) gate the entries as written; they follow the signals, not fills.
    * stdev is the population standard deviation. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bands in standard deviations and range fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED (the long side never fires with the defaults).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427516_bb_fib_as_written"
FAMILY = "bollinger_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40, 10],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "fib_0": 0.0, "fib_100": 1.0, "fib_len": 50}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis, dev = c.rolling(n).mean(), p["mult"] * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    fl = int(p["fib_len"])
    hh, ll = h.rolling(fl).max(), lo.rolling(fl).min()
    rng = hh - ll
    fib_high, fib_low = hh - rng * p["fib_0"], ll + rng * p["fib_100"]

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    def xu(a, b):
        return (a < b) & (a.shift(1) >= b.shift(1))

    long_c = (xo(c, upper) & (lo > fib_low)).to_numpy()
    short_c = (xu(c, lower) & (h < fib_high)).to_numpy()
    long_x, short_x = xu(c, basis).to_numpy(), xo(c, basis).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    lf = sf = False
    for i in range(m):
        new = pos
        if long_c[i] and not sf:
            new, lf, sf = 1, True, False
        if short_c[i] and not lf:
            new, sf, lf = -1, True, False
        if long_x[i]:
            if pos == 1 and new == 1:
                new = 0
            lf = False
        if short_x[i]:
            if pos == -1 and new == -1:
                new = 0
            sf = False
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
