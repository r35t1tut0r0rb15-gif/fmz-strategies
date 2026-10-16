"""Schaff trend cycle (everget), 1-hour bars: the STC (MACD 23 / 50, cycle 10, %D 3 / 3) crossing up through 25 goes long,
crossing down through 75 goes short.
Port of FMZ strategy #430757 "动量跟随的Schaff趋势循环策略Schaff-Trend-Cycle-Momentum-Following-Strategy" (Schaff Trend Cycle).

FMZ source id: 430757

Source
    https://www.fmz.com/strategy/430757 (PineScript v3, FMZ last modified 2023-11-01 16:08:35).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 168-235), MACD 23 / 50, cycle 10, %D 3 / 3, levels 75 / 25
    k = nz(fixnan(stoch(macd, macd, macd, 10))); d = ema(k, 3); kd = nz(fixnan(stoch(d, d, d, 10)))
    stc = clip(ema(kd, 3), 0, 100)
    crossover(stc, 25) -> entry long;  crossunder(stc, 75) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "long" and "short" are the level (25 / 75) or na; strategy.entry reads them as true when not na.
      fixnan carries the last stochastic value over a flat window, nz turns the leading na into 0.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a bounded cycle oscillator.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG430757 (2 members, best partner #440703, Jaccard 0.838); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430757_schaff_trend_cycle"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_length": [23, 12],
    "cycle_length": [10, 20],
}
DEFAULT_PARAMS = {"fast_length": 23, "slow_length": 50, "cycle_length": 10, "d1": 3, "d2": 3, "upper": 75,
                  "lower": 25}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _fixnan_nz(x):
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    v[np.isnan(v)] = 0.0
    return pd.Series(v, index=x.index)


def _stoch_self(x, n):
    ll, hh = x.rolling(n).min(), x.rolling(n).max()
    return 100 * (x - ll) / (hh - ll).replace(0.0, np.nan)


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
    macd = c.ewm(span=int(p["fast_length"]), adjust=False).mean() - c.ewm(span=int(p["slow_length"]), adjust=False).mean()
    n = int(p["cycle_length"])
    k = _fixnan_nz(_stoch_self(macd, n))
    d = k.ewm(span=int(p["d1"]), adjust=False).mean()
    kd = _fixnan_nz(_stoch_self(d, n))
    stc = kd.ewm(span=int(p["d2"]), adjust=False).mean().clip(lower=0.0, upper=100.0)
    lo_l, up_l = float(p["lower"]), float(p["upper"])
    xo = ((stc > lo_l) & (stc.shift(1) <= lo_l)).to_numpy()
    xu = ((stc < up_l) & (stc.shift(1) >= up_l)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if xo[i]:
            pos = 1
        if xu[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
