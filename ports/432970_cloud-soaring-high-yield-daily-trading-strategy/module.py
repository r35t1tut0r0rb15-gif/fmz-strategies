"""Ichimoku tenkan / kijun crosses above the displaced cloud, 1-hour bars, long only: the tenkan 9 crossing above the
kijun 26 with the close above both cloud spans of 26 bars ago goes long; a tenkan cross back under the kijun, or a close
below the lower of those spans, closes it.
Port of FMZ strategy #432970 "Cloud Soaring High Yield Daily Trading Strategy" (High Yield Ichimoku Cloud Strategy).

FMZ source id: 432970

Source
    https://www.fmz.com/strategy/432970 (PineScript v4, FMZ last modified 2023-11-23 10:56:49).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 106-138), tenkan 9, kijun 26, span B 52, displacement 26
    buy = crossover(tenkan, kijun) and close > max(spanA, spanB)[26]
    crossunder(tenkan, kijun) or close < min(spanA, spanB)[26] -> close long (two close calls, same rule)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spans are read 26 bars back ([displacement]): the cloud plotted under the current bar, so
      no future value. The buy and exit conditions exclude each other on one bar.
    * Long only; Opposite entries cannot occur. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku line crosses and cloud position.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432970_ichimoku_cross_above_cloud"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tenkan": [9, 20],
    "kijun": [26, 60],
}
DEFAULT_PARAMS = {"tenkan": 9, "kijun": 26, "span_b": 52, "disp": 26}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def mid(n):
        return (h.rolling(int(n)).max() + lo.rolling(int(n)).min()) / 2

    ten, kij = mid(p["tenkan"]), mid(p["kijun"])
    sa, sb = (ten + kij) / 2, mid(p["span_b"])
    d = int(p["disp"])
    top = pd.concat([sa, sb], axis=1).max(axis=1, skipna=False).shift(d)
    bot = pd.concat([sa, sb], axis=1).min(axis=1, skipna=False).shift(d)
    up = (ten > kij) & (ten.shift(1) <= kij.shift(1))
    dn = (ten < kij) & (ten.shift(1) >= kij.shift(1))
    buy = (up & (c > top)).to_numpy()
    ex = (dn | (c < bot)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 0 and buy[i]:
            pos = 1
        elif pos == 1 and ex[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
