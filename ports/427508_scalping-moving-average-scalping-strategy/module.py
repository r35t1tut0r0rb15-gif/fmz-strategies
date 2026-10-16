"""MA scalping, long only: SMA 9 crossing above SMA 50 while the averages are stacked downwards
(SMA 50 < SMA 100 < SMA 200) goes long; SMA 9 crossing above SMA 200 closes the long.
Port of FMZ strategy #427508 "Moving Average Scalping Strategy".

FMZ source id: 427508

Source
    https://www.fmz.com/strategy/427508 (PineScript v4, FMZ last modified 2023-09-21 20:41:15).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 195-230), SMA 9 / 50 / 100 / 200
    crossover(sma9, sma50) and sma50 < sma100 < sma200 -> entry long
    crossover(sma9, sma200) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 2 % / 8 % stop and target levels are computed but no order uses them: not ported (stored).
    * window() is the constant true. Long only; entries only from flat.
    * FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the unused stop / target levels stored in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427508_ma_scalping_long"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "signal": [9, 5, 20],
    "fast": [50, 30],
}
DEFAULT_PARAMS = {"signal": 9, "fast": 50, "mid": 100, "slow": 200}


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
    s, f, mi, sl = (c.rolling(int(p[k])).mean() for k in ("signal", "fast", "mid", "slow"))
    entry = ((s > f) & (s.shift(1) <= f.shift(1)) & (f < mi) & (mi < sl)).to_numpy()
    exit_ = ((s > sl) & (s.shift(1) <= sl.shift(1))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and entry[i]:
            le[i], pos = True, 1
        elif pos == 1 and exit_[i]:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
