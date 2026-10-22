"""Chande-style momentum against its WMA zone, 1-hour bars: the WMA 9 of the 9-bar momentum over the summed absolute changes above 60 holds a long, below -60 a short; reversing; the entry is sent on every
bar of the state.
Port of FMZ strategy #440005 "基于CMO和WMA的双均线交易策略CMO-and-WMA-Based-Dual-Moving-Average-Trading-Strategy" (CMO & WMA Backtest ver 2.0).

FMZ source id: 440005

Source
    https://www.fmz.com/strategy/440005 (PineScript v3, FMZ last modified 2024-01-25 17:44:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 149-192), length 9; WMA 9; buy zone 60, sell zone -60; reverse off
    nRes = 100 (close - close[9]) / (sma(|close - close[1]|, 9) x 9);  xWMACMO = wma(nRes, 9);  pos = xWMACMO > 60 ? 1 : xWMACMO < -60 ? -1 : previous

Interpretation choices (Pine rules in SURVEY_README.md)
    * A same-side entry while in the position is ignored. strategy.entry reverses: REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, momentum ratio zones.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430117 (4 members, best partner #433583, Jaccard 0.726); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440005_hpotter_cmo_wma_zone_state"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [9, 14],
    "buy_zone": [60.0, 40.0],
}
DEFAULT_PARAMS = {"length": 9, "buy_zone": 60.0, "length_wma": 9}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    with np.errstate(divide="ignore", invalid="ignore"):
        res = 100 * (c - c.shift(n)) / (c.diff().abs().rolling(n).mean() * n)
    res = res.where(np.isfinite(res))
    w = _wma(res, int(p["length_wma"])).to_numpy()
    bz = float(p["buy_zone"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if w[i] > bz:
            pos = 1
        elif w[i] < -bz:
            pos = -1
        tgt[i] = pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(tgt == 1, index=ix), false, pd.Series(tgt == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
