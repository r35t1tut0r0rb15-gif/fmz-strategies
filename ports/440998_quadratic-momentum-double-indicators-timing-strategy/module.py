"""Four SuperTrends in agreement, 5-minute bars: all four trends up goes long, all down goes short; any of the four flipping closes everything.
Port of FMZ strategy #440998 "Quadratic Momentum Double Indicators Timing Strategy" (EQM Strategy [presentTrading]).

FMZ source id: 440998

Source
    https://www.fmz.com/strategy/440998 (PineScript v5, FMZ last modified 2024-02-04 15:53:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-216), direction Both; SuperTrends ATR 7 x 4, 14 x 3.618, 21 x 3.5, 28 x 3.382 on close
    supertrend: up = hl2 - m atr, dn = hl2 + m atr;  up = max(up, up[1]) if close > up[1] and close[1] > up[1];  dn = min(dn, dn[1]) if close < dn[1] and close[1] < dn[1];  trend = close > dn[1] ? 1 : close < up[1] ? -1 : trend[1] (nz(.., 0) starts)
    all trends 1 -> entry Long;  all -1 -> entry Short;  any trend != trend[1] -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SuperTrend is ported as written (it is not the usual flip rule: the close above the previous
      upper line sets 1, below the previous lower line -1), with its nz(.., 0) starts, so during the ATR
      warm-up the trend reads 1. close_all after an entry on the same bar leaves the bar flat (as #430380),
      so a position opens on the first bar of agreement without a flip and ends at the next flip. A flip
      always comes between opposite agreements, so opposite entries cannot occur (entries only from flat).
      The gradient plots are not used. No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, four SuperTrend states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440998_four_supertrend_agreement_flip_exit"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_length1": [7, 14],
    "multiplier1": [4.0, 3.0],
}
DEFAULT_PARAMS = {"atr_length1": 7, "multiplier1": 4.0, "atr_length2": 14, "multiplier2": 3.618,
                  "atr_length3": 21, "multiplier3": 3.5, "atr_length4": 28, "multiplier4": 3.382}


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


def _trend(bars_df, n, mult):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n)
    hl2 = (h + lo) / 2
    ub = (hl2 - mult * atr).to_numpy()
    db = (hl2 + mult * atr).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    t = np.ones(m, dtype=np.int8)
    pu = pd_ = np.nan
    tp = 1
    for i in range(m):
        pun = 0.0 if np.isnan(pu) else pu
        pdn = 0.0 if np.isnan(pd_) else pd_
        cp = cv[i - 1] if i > 0 else np.nan
        u = ub[i]
        if cv[i] > pun and cp > pun:
            u = np.nan if np.isnan(u) else max(u, pun)
        d = db[i]
        if cv[i] < pdn and cp < pdn:
            d = np.nan if np.isnan(d) else min(d, pdn)
        tp = 1 if cv[i] > pdn else (-1 if cv[i] < pun else tp)
        t[i] = tp
        pu, pd_ = u, d
    return t


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ts = [_trend(bars_df, int(p[f"atr_length{j}"]), float(p[f"multiplier{j}"])) for j in (1, 2, 3, 4)]
    allup = np.logical_and.reduce([t == 1 for t in ts])
    alldn = np.logical_and.reduce([t == -1 for t in ts])
    flip = np.zeros(len(allup), dtype=bool)
    for t in ts:
        flip[1:] |= t[1:] != t[:-1]
    m = len(allup)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if allup[i] and pos != 1:
            pos = 1
        elif alldn[i] and pos != -1:
            pos = -1
        if flip[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
