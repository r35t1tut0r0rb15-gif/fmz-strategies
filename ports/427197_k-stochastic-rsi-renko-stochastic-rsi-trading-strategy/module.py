"""Stochastic RSI cross: K (SMA 5 of the 3-bar stochastic of RSI 20) crossing above D (SMA 2 of K)
goes long, crossing below goes short (always in the market after the first cross).
Port of FMZ strategy #427197 "Renko Stochastic RSI Trading Strategy".

FMZ source id: 427197

Source
    https://www.fmz.com/strategy/427197 (PineScript v3, FMZ last modified 2023-09-18 22:33:09).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 197-214), RSI 20, stoch 3, smooth K 5, D 2
    k = sma(stoch(rsi, rsi, rsi, 3), 5); d = sma(k, 2)
    crossover(k, d) -> entry long; crossunder(k, d) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Renko" is only in the description: the code reads ordinary bars, and the FMZ backtest runs
      on 3-hour time bars. The port uses those (a Renko chart is not a bar size the contract has).
    * stoch(x, x, x, n) is the stochastic of the RSI series itself (current bar included).
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: commission setting stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427197_stoch_rsi_cross"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [20, 14],
    "stoch_length": [3, 14],
    "smooth_k": [5, 3],
}
DEFAULT_PARAMS = {"rsi_length": 20, "stoch_length": 3, "smooth_k": 5, "smooth_d": 2}


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


def _rsi(close, n):
    ch = close.diff()
    up = _rma(ch.clip(lower=0), n).to_numpy()
    dn = _rma((-ch).clip(lower=0), n).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn)))
    val[np.isnan(up) | np.isnan(dn)] = np.nan
    return pd.Series(val, index=close.index)


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
    r = _rsi(bars_df["close"], int(p["rsi_length"]))
    n = int(p["stoch_length"])
    lo, hi = r.rolling(n).min(), r.rolling(n).max()
    st = 100 * (r - lo) / (hi - lo)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    long_c = ((k > d) & (k.shift(1) <= d.shift(1))).to_numpy()
    short_c = ((k < d) & (k.shift(1) >= d.shift(1))).to_numpy()
    m = len(k)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
