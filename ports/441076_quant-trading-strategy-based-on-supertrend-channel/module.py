"""SuperTrend (ATR 7 x 7) direction flips, 2-hour bars: the direction turning up goes long, turning down goes short; reversing.
Port of FMZ strategy #441076 "Quant Trading Strategy Based on SuperTrend Channel" (SuperTrend Strategy).

FMZ source id: 441076

Source
    https://www.fmz.com/strategy/441076 (PineScript v4, FMZ last modified 2024-02-05 13:57:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 120-172), ATR period 7, multiplier 7; labels shown
    longStop = hl2 - 7 atr(7), ratcheted up while close[1] > longStopPrev;  shortStop = hl2 + 7 atr, ratcheted down while close[1] < shortStopPrev
    dir = dir == -1 and close > shortStopPrev ? 1 : dir == 1 and close < longStopPrev ? -1 : dir;  dir flips to 1 -> entry long;  flips to -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ATR-stops SuperTrend is ported as written (nz(x[1], x) starts, direction starting at 1). Pine's
      atr is the RMA of the true range. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ =
      "2h" from the backtest header (bars on UTC multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend direction flips.
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

NAME = "fmz_441076_atr_stops_supertrend_7x7_flip_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [7, 14],
    "mult": [7.0, 3.0],
}
DEFAULT_PARAMS = {"length": 7, "mult": 7.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a = (float(p["mult"]) * _rma(tr, int(p["length"]))).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    d = np.ones(m, dtype=np.int8)
    ls = ss = np.nan
    dr = 1
    for i in range(m):
        lc, sc = hl2[i] - a[i], hl2[i] + a[i]
        lp = lc if np.isnan(ls) else ls
        sp = sc if np.isnan(ss) else ss
        cp = cv[i - 1] if i > 0 else np.nan
        ls = max(lc, lp) if cp > lp else lc
        ss = min(sc, sp) if cp < sp else sc
        if dr == -1 and cv[i] > sp:
            dr = 1
        elif dr == 1 and cv[i] < lp:
            dr = -1
        d[i] = dr
    prev = np.concatenate(([1], d[:-1]))
    ix = bars_df.index
    up = pd.Series((d == 1) & (prev == -1), index=ix)
    dn = pd.Series((d == -1) & (prev == 1), index=ix)
    false = pd.Series(False, index=ix)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
