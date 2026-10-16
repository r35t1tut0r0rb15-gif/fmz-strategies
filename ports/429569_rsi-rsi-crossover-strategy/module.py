"""Smoothed RSI cross state, 4-hour bars: EMA 20 of RSI 5 crossing above EMA 50 of RSI 5 switches to long, crossing
below switches to short; the side is held until the next cross.
Port of FMZ strategy #429569 "RSI金叉死叉策略RSI-Crossover-Strategy" (RSI Cross [xaurr]).

FMZ source id: 429569

Source
    https://www.fmz.com/strategy/429569 (PineScript v4, FMZ last modified 2023-10-18 11:44:45).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 228-264), RSI 5, smoothing EMA 20 / 50 (30 / 70 drawn only)
    pos = crossover(fast, slow) ? 1 : crossunder(fast, slow) ? -1 : pos[1]
    pos == 1 -> entry long; pos == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 30 / 70 levels are drawn only. strategy.entry reverses: REVERSAL INTENDED.
      FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI averages only.
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

NAME = "fmz_429569_rsi_ema_cross_state"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [50, 30],
}
DEFAULT_PARAMS = {"period": 5, "fast": 20, "slow": 50}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r = _rsi(bars_df["close"], int(p["period"]))
    f = r.ewm(span=int(p["fast"]), adjust=False).mean()
    s = r.ewm(span=int(p["slow"]), adjust=False).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    m = len(r)
    pos = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        pos[i] = q
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(pos == 1, index=idx), false, pd.Series(pos == -1, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
