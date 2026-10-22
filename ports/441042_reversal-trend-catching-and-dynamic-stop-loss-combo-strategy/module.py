"""HPotter combo of the 123 reversal and Kase Dev Stops, 1-hour bars: long when both states are long, short when both are short, flat otherwise; reversing.
Port of FMZ strategy #441042 "Reversal Trend Catching and Dynamic Stop Loss Combo Strategy" (Combo Backtest 123 Reversal & Kase Dev Stops).

FMZ source id: 441042

Source
    https://www.fmz.com/strategy/441042 (PineScript v4, FMZ last modified 2024-02-05 09:54:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-192), 123: stochastic 14, K smoothing 1, D 3, level 50; Kase Dev Stops length 30, trade from level 4; reverse off
    123: close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50 -> 1;  mirrored -> -1;  else previous
    Kase: RWH = (high - low[30]) / (atr(30) sqrt(30)), RWL = (high[30] - low) / same, Pk = wma(RWH - RWL, 3);  AVTR / SD = sma / stdev(highest(high, 2) - lowest(low, 2), 20)
    Val4 = Pk > 0 ? highest(high - AVTR - 3 SD, 20) : lowest(low + AVTR + 3 SD, 20);  pos = close < Val4 ? -1 : 1;  both 1 -> entry Long, both -1 -> entry Short, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both states are ported as written: the 123 state keeps its previous value, the Kase state reads 1
      whenever its level is na (close < na is false). Pine's stdev is the population deviation, its atr
      the RMA of the true range. The combined state is a level; disagreement closes. REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close pattern, stochastic and Kase levels.
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

NAME = "fmz_441042_reversal123_kase_dev_stops_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_kds": [30, 20],
}
DEFAULT_PARAMS = {"length": 14, "length_kds": 30, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "level_kds": 4, "reverse": False}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    vfast = st.rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    up_ = ((c2 < c1) & (c > c1) & (vfast < vslow) & (vfast > lvl)).to_numpy()
    dn_ = ((c2 > c1) & (c < c1) & (vfast > vslow) & (vfast < lvl)).to_numpy()
    k = int(p["length_kds"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    den = _rma(tr, k) * np.sqrt(k)
    rwh = (h - lo.shift(k)) / den
    rwl = (h.shift(k) - lo) / den
    pk = _wma(rwh - rwl, 3)
    rng = h.rolling(2).max() - lo.rolling(2).min()
    avtr = rng.rolling(20).mean()
    sd = rng.rolling(20).std(ddof=0)
    f = int(p["level_kds"]) - 1   # level 4 -> 3 SD, 3 -> 2, 2 -> 1, 1 -> 0
    hi_v = (h - avtr - f * sd).rolling(20).max()
    lo_v = (lo + avtr + f * sd).rolling(20).min()
    val = pd.Series(np.where(pk > 0, hi_v, lo_v), index=c.index)
    pk_state = np.where(c < val, -1, 1)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        tgt[i] = 1 if (p123 == 1 and pk_state[i] == 1) else (-1 if (p123 == -1 and pk_state[i] == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
