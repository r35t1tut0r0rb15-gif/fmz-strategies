"""A recursive average of one-bar changes with the SMA 50 trend, hourly bars: a positive average with the close over the SMA goes long, a negative one under it goes short; reversing. As written the "KNN" search compares the window with itself, so every neighbour is index 0 and the average is A = A[1] / k + (close - close[1]).
Port of FMZ strategy #473319 "KNN自适应参数化趋势跟踪策略-KNN-Based-Adaptive-Parametric-Trend-Following-Strategy" (Trend Following Strategy with KNN).

FMZ source id: 473319

Source
    https://www.fmz.com/strategy/473319 (PineScript v6, FMZ last modified 2024-11-29 10:54:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 138-200), K 5, window 20, SMA 50; commission 0.03 %, cash size
    features = close[0..19]; distance(var) += (close[j] - features[j])^2 = 0; neighbours = index 0 (var min_index); average_change(var) := (average_change + k x (close - close[1])) / k;  avg > 0 and close > ma -> entry Long;  avg < 0 and close < ma -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The window is compared with itself, so every distance is 0 and the var-declared minimum search
      keeps index 0 for all k neighbours; the var index and the var running average are never reset,
      so from the first bar with 20 bars of data the average is the recursion above (k neighbours each
      add close - close[1], then the sum is divided by k), as written. There is no exit: positions end
      at the opposite entry. REVERSAL INTENDED. The cash size and commission are not ported. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, recursive change average with an SMA filter, as written.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: cash size and commission stored, not ported.
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

NAME = "fmz_473319_knn_self_window_recursive_change_sma50_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "k": [5, 3],
    "ma_length": [50, 100],
}
DEFAULT_PARAMS = {"k": 5, "ma_length": 50, "window_size": 20}


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
    k, w = int(p["k"]), int(p["window_size"])
    ma = c.rolling(int(p["ma_length"])).mean().to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    avg = 0.0
    for i in range(w - 1, m):
        if i >= 2:                               # index + 1 < bar_index with index 0
            avg = (avg + k * (cv[i] - cv[i - 1])) / k
        else:
            avg = avg / k
        if avg > 0 and cv[i] > ma[i]:
            le[i] = True
        elif avg < 0 and cv[i] < ma[i]:
            se[i] = True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
