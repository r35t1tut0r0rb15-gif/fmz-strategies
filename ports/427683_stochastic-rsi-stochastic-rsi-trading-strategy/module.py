"""HPotter Stochastic RSI: the smoothed stochastic of RSI 14 above 80 holds a long, below 20 a short;
between the bands the last side is kept.
Port of FMZ strategy #427683 "Stochastic RSI Trading Strategy".

FMZ source id: 427683

Source
    https://www.fmz.com/strategy/427683 (PineScript v2, FMZ last modified 2023-09-23 15:59:22).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 181-212), bands 80 / 20, RSI 14, stoch 14, K 3, D 3
    k = sma(stoch(rsi, rsi, rsi, 14), 3)
    pos = k > 80 ? 1 : k < 20 ? -1 : nz(pos[1], 0) -> entry long / entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Trade reverse" (default false) is fixed off; D is drawn only.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_427683_hpotter_stoch_rsi_bands"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "top": [80, 70],
    "low": [20, 30],
    "length_rsi": [14, 7],
}
DEFAULT_PARAMS = {"top": 80, "low": 20, "length_rsi": 14, "length_stoch": 14, "smooth_k": 3}


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
    c = bars_df["close"]
    d = c.diff()
    n = int(p["length_rsi"])
    up, dn = _rma(d.clip(lower=0), n), _rma(-d.clip(upper=0), n)
    rsi = 100 - 100 / (1 + up / dn)
    ls = int(p["length_stoch"])
    rl, rh = rsi.rolling(ls).min(), rsi.rolling(ls).max()
    k = (100 * (rsi - rl) / (rh - rl)).rolling(int(p["smooth_k"])).mean().to_numpy()
    m = len(k)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if k[i] > p["top"]:
            pos = 1
        elif k[i] < p["low"]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
