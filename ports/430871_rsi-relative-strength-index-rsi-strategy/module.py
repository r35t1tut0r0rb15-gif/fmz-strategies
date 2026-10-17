"""RSI 12 momentum (HPotter), 1-hour bars: RSI above 70 holds a long, under 30 holds a short (as written: strength is
bought, weakness sold).
Port of FMZ strategy #430871 "相对强弱指标RSI策略Relative-Strength-Index-RSI-Strategy" (Strategy RSI).

FMZ source id: 430871

Source
    https://www.fmz.com/strategy/430871 (PineScript v2, FMZ last modified 2023-11-02 15:54:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 155-183), RSI 12, 30 / 70
    rsi(close, 12) > 70 -> 1 (entry long);  rsi < 30 -> -1 (entry short);  else pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * The overbought level opens longs and the oversold level shorts, as written. "Trade reverse"
      defaults to false and is fixed. strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels.
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

NAME = "fmz_430871_rsi_momentum_levels"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [12, 24],
    "overbought": [70, 60],
}
DEFAULT_PARAMS = {"length": 12, "overbought": 70}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


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
    r = _rsi(bars_df["close"], int(p["length"])).to_numpy()
    ob = float(p["overbought"])
    m = len(r)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if r[i] > ob:
            pos = 1
        elif r[i] < 100 - ob:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
