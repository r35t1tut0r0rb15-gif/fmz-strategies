"""Distance oscillator, 4-hour bars: the close's percent distance from the 20-bar channel midpoint is
smoothed with HMA 50; the HMA crossing above its own value 12 bars ago goes long, crossing below goes
short.
Port of FMZ strategy #428629 "Dual Moving Average Crossover Trading Strategy" (Distance Oscillator - evo).

FMZ source id: 428629

Source
    https://www.fmz.com/strategy/428629 (PineScript v4, FMZ last modified 2023-10-07 16:39:01).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 193-249), channel 20, Hull 50, lag 12, Percent format
    osc = (close - (highest(20) + lowest(20)) / 2) / close x 100; ma = hma(osc, 50)
    crossover(ma, ma[12]) -> entry long; crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Defaults kept: Percent format, Hull average. strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, percent distance and MA lengths.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_428629_distance_oscillator_hma"
FAMILY = "hull_ma"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 25],
    "lagg": [12, 6],
}
DEFAULT_PARAMS = {"example_length": 20, "length": 50, "lagg": 12}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


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
    e = int(p["example_length"])
    mid = (h.rolling(e).max() + lo.rolling(e).min()) / 2
    osc = (c - mid) / c * 100
    n = int(p["length"])
    ma = _wma(2 * _wma(osc, n // 2) - _wma(osc, n), int(round(np.sqrt(n))))
    lag = ma.shift(int(p["lagg"]))
    up = ((ma > lag) & (ma.shift(1) <= lag.shift(1))).to_numpy()
    dn = ((ma < lag) & (ma.shift(1) >= lag.shift(1))).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
