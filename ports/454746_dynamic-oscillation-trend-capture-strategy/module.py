"""MACD 12 / 26 / 9 crossings coloured by a Hilo activator (4), 3-hour bars: a MACD cross up with the close at or over the activator goes long, a cross down with the activator over the close goes short; reversing.
Port of FMZ strategy #454746 "Dynamic Oscillation Trend Capture Strategy" (Hilo MACD Strategy).

FMZ source id: 454746

Source
    https://www.fmz.com/strategy/454746 (PineScript v5, FMZ last modified 2024-06-21 15:40:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 173-211), Hilo period 4 (activator by valuewhen, 4 occurrences back); MACD 12 / 26 / 9
    activator = valuewhen(close > hh[1] and close[1] < hh[2], hh, 4), else the low versions;  green = not (activator > close)
    crossover(macd, signal) and green -> entry Long;  crossunder and red -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.valuewhen with occurrence 4 returns the value at the fifth most recent bar where its condition
      held; the activator falls back to the low-based conditions while na, as written. 'Green' is any
      bar where the activator is not over the close (na included). There is no exit: positions end at
      the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "3h" from the backtest header
      (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings with a Hilo filter.
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

NAME = "fmz_454746_macd_cross_hilo_activator_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hilo_len": [4, 8],
    "fast": [12, 8],
    "slow": [26, 21],
}
DEFAULT_PARAMS = {"hilo_len": 4, "fast": 12, "slow": 26, "signal": 9}


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


def _valuewhen(cond, src, occ):
    """Pine valuewhen(cond, src, occ): src at the (occ + 1)-th most recent bar where cond held."""
    out = np.full(len(src), np.nan)
    hits = []
    for i in range(len(src)):
        if cond[i]:
            hits.append(src[i])
        if len(hits) > occ:
            out[i] = hits[-1 - occ]
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["hilo_len"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    c1 = c.shift(1)
    k1 = ((c > hh.shift(1)) & (c1 < hh.shift(2))).to_numpy()
    k2 = ((c < ll.shift(1)) & (c1 > ll.shift(2))).to_numpy()
    k3 = ((c1 > hh.shift(1)) & (c < ll.shift(1))).to_numpy()
    hv, lv = hh.to_numpy(), ll.to_numpy()
    act = _valuewhen(k1, hv, n)
    a2, a3 = _valuewhen(k2, lv, n), _valuewhen(k3, lv, n)
    act = np.where(np.isnan(act), a2, act)
    act = np.where(np.isnan(act), a3, act)
    cv = c.to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        red = act > cv
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    up = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    dn = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(up & ~red, index=ix), false, pd.Series(dn & red, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
