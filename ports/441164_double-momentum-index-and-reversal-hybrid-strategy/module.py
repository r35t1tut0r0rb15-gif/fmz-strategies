"""HPotter combo of the 123 reversal and Wilder's Commodity Selection Index, 1-hour bars: long when the 123 state is long and the CSI is under its 14-bar SMA, short when the 123 state is short and the CSI
above it, flat otherwise; reversing.
Port of FMZ strategy #441164 "Double Momentum Index and Reversal Hybrid Strategy" (Combo Strategy 123 Reversal & Commodity Selection Index).

FMZ source id: 441164

Source
    https://www.fmz.com/strategy/441164 (PineScript v4, FMZ last modified 2024-02-06 12:22:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 154-239), 123: stochastic 14, K smoothing 1, D 3, level 50; CSI 14 (point value 50, margin 3000, commission 10); reverse off
    123: close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50 -> 1;  mirrored -> -1;  else previous
    CSI = K atr(14) (adx + adx[14]) / 2, K = 100 x 50 / sqrt(3000) / (150 + 10);  CSI < sma(CSI, 14) -> 1, > -> -1, else previous;  both 1 -> entry Long, both -1 -> entry Short, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both states are ported as written; the ADX is the script's fADX (fixnan on the DIs; the first
      directional movement reads 0, the first true range na). K is a positive constant, so it does not change
      the comparison. The combined state is a level; disagreement closes. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close pattern, stochastic and CSI states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (the CSI's point value, margin and commission are only its constant).
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

NAME = "fmz_441164_reversal123_csi_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_csi": [14, 28],
}
DEFAULT_PARAMS = {"length": 14, "length_csi": 14, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "point_value": 50.0, "margin": 3000.0, "commission": 10.0, "reverse": False}


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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


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
    k = int(p["length_csi"])
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trur = _rma(tr, k)
    plus = _fixnan(100 * _rma(pdm, k) / trur)
    minus = _fixnan(100 * _rma(mdm, k) / trur)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), k)
    kk = 100 * (float(p["point_value"]) / np.sqrt(float(p["margin"])) / (150 + float(p["commission"])))
    tr_atr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    csi = kk * _rma(tr_atr, k) * (adx + adx.shift(k)) * 0.5
    ma = csi.rolling(k).mean()
    cu, cd = (csi < ma).to_numpy(), (csi > ma).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = pcs = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if cu[i]:
            pcs = 1
        elif cd[i]:
            pcs = -1
        tgt[i] = 1 if (p123 == 1 and pcs == 1) else (-1 if (p123 == -1 and pcs == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
