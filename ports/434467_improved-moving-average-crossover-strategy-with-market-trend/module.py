"""Double SMA crosses on one bar, 1-minute bars: the SMA 9 crossing above the SMA 21 on the same bar as the SMA 21 crosses
above the SMA 50 goes long (closing a short); the mirror crosses go short (closing a long); held otherwise.
Port of FMZ strategy #434467 "Improved Moving Average Crossover Strategy with Market Trend Guidance" (Improved Moving Average Crossover Strategy).

FMZ source id: 434467

Source
    https://www.fmz.com/strategy/434467 (PineScript v5, FMZ last modified 2023-12-06 16:29:52).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 163-198), SMA 9 / 21 / 50
    buy = crossover(sma9, sma21) and crossover(sma21, sma50) -> entry long, close short
    sell = crossunder(sma9, sma21) and crossunder(sma21, sma50) -> close long, entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both crosses must happen on the same bar, as written. strategy.entry reverses (the paired
      closes act on the same side): REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crosses.
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

NAME = "fmz_434467_double_sma_cross_same_bar"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "trend": [50, 100],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "trend": 50}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s, t = (c.rolling(int(p[k])).mean() for k in ("fast", "slow", "trend"))
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))  # noqa: E731
    buy = (xo(f, s) & xo(s, t)).to_numpy()
    sell = (xo(s, f) & xo(t, s)).to_numpy()
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if buy[i]:
            q = 1
        elif sell[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
