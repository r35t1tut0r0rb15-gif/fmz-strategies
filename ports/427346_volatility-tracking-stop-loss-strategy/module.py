"""HPotter volatility system: a Wilder-smoothed ATR(10) below its SMA 26 (volatility falling) goes
long, above it goes short (always in the market after the first signal).
Port of FMZ strategy #427346 "Volatility Tracking Stop Loss Strategy".

FMZ source id: 427346

Source
    https://www.fmz.com/strategy/427346 (PineScript v2, FMZ last modified 2023-09-20 11:31:12).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 129-143), length 10, MA 26, reverse off
    nRes = ((10 - 1) nz(nRes[1], 0) + atr(10)) / 10; m = sma(nRes, 26)
    pos = nRes < m ? 1 : nRes > m ? -1 : pos[1] -> entries on pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * nRes starts from 0 at the first bar with an ATR (nz), as written.
    * The title's "stop loss" is not in the code: there is no stop. REVERSAL INTENDED.
    * FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR compared with its own average (scale-free).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427346_hpotter_volatility_regime"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "length_ma": [26, 13, 52],
}
DEFAULT_PARAMS = {"length": 10, "length_ma": 26}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


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
    n = int(p["length"])
    pc = bars_df["close"].shift(1)
    tr = pd.concat([bars_df["high"] - bars_df["low"], (bars_df["high"] - pc).abs(), (bars_df["low"] - pc).abs()],
                   axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, n).to_numpy()
    m = len(atr)
    res = np.full(m, np.nan)
    prev = np.nan
    for i in range(m):
        base = 0.0 if np.isnan(prev) else prev
        res[i] = ((n - 1) * base + atr[i]) / n
        prev = res[i]
    ma = pd.Series(res, index=bars_df.index).rolling(int(p["length_ma"])).mean().to_numpy()
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if res[i] < ma[i]:
            pos = 1
        elif res[i] > ma[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
