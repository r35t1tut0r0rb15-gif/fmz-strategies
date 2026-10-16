"""MACD turn + RSI, hourly bars: a rising EMA 8 - EMA 24 difference with RSI 7 under 36 goes long; a
falling difference with RSI 7 over 56 goes short.
Port of FMZ strategy #428103 "Dual EMA with RSI Trend Following Strategy" (MACD + RSI).

FMZ source id: 428103

Source
    https://www.fmz.com/strategy/428103 (PineScript v2, FMZ last modified 2023-09-28 16:17:53).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 171-200), EMA 8 / 24, RSI 7, threshold 0.2
    div = ema8 - ema24; long when div > div[1] and rsi < 30 x 1.2; short when div < div[1] and rsi > 70 x 0.8

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths and RSI levels.
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

NAME = "fmz_428103_macd_turn_rsi"
FAMILY = "macd_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_threshold": [0.2, 0.1],
    "len": [7, 14],
}
DEFAULT_PARAMS = {"len1": 8, "len2": 24, "len": 7, "rsi_threshold": 0.2}


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
    div = c.ewm(span=int(p["len1"]), adjust=False).mean() - c.ewm(span=int(p["len2"]), adjust=False).mean()
    d = c.diff()
    n = int(p["len"])
    up, dn = _rma(d.clip(lower=0), n), _rma(-d.clip(upper=0), n)
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())
    t = p["rsi_threshold"]
    long_s = ((div > div.shift(1)) & (rsi < 30 * (1 + t))).to_numpy()
    short_s = ((div < div.shift(1)) & (rsi > 70 * (1 - t))).to_numpy()
    m = len(long_s)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_s[i]:
            pos = 1
        elif short_s[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
