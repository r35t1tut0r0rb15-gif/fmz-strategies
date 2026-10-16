"""MACD TrueLevel, long only, 4-hour bars: a MACD cross up, or the close crossing above the 12th
TrueLevel lower band (linear regression of 2646 bars minus one stdev), goes long; a MACD cross down or
the close crossing under the 12th upper band closes it.
Port of FMZ strategy #428581 "MACD TrueLevel Strategy".

FMZ source id: 428581

Source
    https://www.fmz.com/strategy/428581 (PineScript v4, FMZ last modified 2023-10-07 10:23:01).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 168-375), MACD 12/26/9, bands 1..14 (lengths 126 .. 4284), entry / exit band 12
    band_k = linreg(close, len_k, 0) -+ 1 x stdev(close, len_k)
    long = crossover(macd, signal) or crossover(close, lower_band[entry]); exit long = crossunder(macd, signal)
           or crossunder(close, upper_band[exit]); shorts off ("Enable Long and Short" false)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the selected entry / exit bands reach the orders (the TrueLevel max / min are drawn).
    * An entry and a close on one bar: the close acts only on an open position. Long only.
    * Band 12 is 2646 bars long (about 441 days of 4-hour bars): long warm-up, as written.
    * FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, regression bands in standard deviations.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG428581 (2 members, best partner #431501, Jaccard 0.855); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428581_macd_truelevel_long"
FAMILY = "macd_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

LENGTHS = (126, 189, 252, 378, 504, 630, 756, 1008, 1260, 1638, 2016, 2646, 3276, 4284)
GRID = {
    "entry_band": [12, 6],
    "exit_band": [12, 6],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "entry_band": 12, "exit_band": 12, "mult": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _linreg_end(y, L):
    """Pine linreg(y, L, 0): the least-squares line's value at the current bar, via running sums."""
    v = y.to_numpy(dtype=float)
    k = np.arange(len(v), dtype=float)
    cy = np.concatenate(([0.0], np.cumsum(v)))
    cky = np.concatenate(([0.0], np.cumsum(k * v)))
    out = np.full(len(v), np.nan)
    x_sum = L * (L - 1) / 2
    xx_sum = (L - 1) * L * (2 * L - 1) / 6
    den = L * xx_sum - x_sum ** 2
    for t in range(L - 1, len(v)):
        s0 = t - L + 1
        sy = cy[t + 1] - cy[s0]
        sxy = (cky[t + 1] - cky[s0]) - s0 * sy
        slope = (L * sxy - x_sum * sy) / den
        out[t] = (sy - slope * x_sum) / L + slope * (L - 1)
    return pd.Series(out, index=y.index)


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
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    le_len, lx_len = LENGTHS[int(p["entry_band"]) - 1], LENGTHS[int(p["exit_band"]) - 1]
    lower = _linreg_end(c, le_len) - p["mult"] * c.rolling(le_len).std(ddof=0)
    upper = _linreg_end(c, lx_len) + p["mult"] * c.rolling(lx_len).std(ddof=0)
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))
    xu = lambda a, b: (a < b) & (a.shift(1) >= b.shift(1))
    enter = (xo(macd, sig) | xo(c, lower)).to_numpy()
    exit_ = (xu(macd, sig) | xu(c, upper)).to_numpy()
    m = len(enter)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if start == 0 and enter[i]:
            pos = 1
        if start == 1 and exit_[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
