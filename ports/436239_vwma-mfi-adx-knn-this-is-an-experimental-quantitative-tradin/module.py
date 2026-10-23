"""Hourly bars: the VWMA 13 of the open crossing over the VWMA 19 goes long when a kNN vote (the 23 nearest stored crossings in ADX 13 / 6 and MFI 13 space, each labelled by whether the open rose until the next crossing) is not negative; crossing under goes short when the vote is negative; reversing.
Port of FMZ strategy #436239 "基于VWMA和MFI-ADX的kNN机器学习量化交易策略This-is-an-experimental-quantitative-trading-strategy" (VWMA with kNN Machine Learning: MFI/ADX (lastguru)).

FMZ source id: 436239

Source
    https://www.fmz.com/strategy/436239 (PineScript v4, FMZ last modified 2023-12-22 14:13:27).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 143-277), source open; VWMA 13 / 19; DMI 13, smoothing 6; MFI 13 of ohlc4; k = 23
    on every crossing: _knnStore(adx, mfi, open) pushes the PREVIOUS crossing's (adx, mfi) with label open >= previous open ? 1 : -1;  filter = sum of the labels of the k nearest stored points
    crossover(vwma13, vwma19) and filter >= 0 -> entry Long;  crossunder and filter < 0 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stores start with one (0, 0, label 0) point. On a crossing bar the previous crossing's point is
      stored (its label known now) before the vote, so the current crossing never votes on itself. The
      neighbours are all stored points whose distance is at most the k-th smallest (ties included), as
      written. The DMI uses the script's own Wilder average started from 0 (nz) and fixnan; the MFI is the
      bare formula (the discarded "if" lines, as #431959). Points with an na feature never count as near.
      The MFI and both VWMAs read volume as ratios. REVERSAL INTENDED. 100 % of equity is sizing. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, VWMA crossings filtered by a kNN vote on past crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in both VWMAs of the open and the MFI 13; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436239_vwma13_19_cross_knn_adx_mfi_vote_reversal"
FAMILY = "machine_learning_vote"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "knn": [23, 10],
    "fast": [13, 8],
}
DEFAULT_PARAMS = {"fast": 13, "slow": 19, "filter_len": 13, "smooth": 6, "knn": 23}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _wilder0(x, n):
    """The script's _rma: out := ((n - 1) x nz(out[1]) + x) / n."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    prev = np.nan
    for i in range(len(v)):
        out[i] = ((n - 1) * (0.0 if np.isnan(prev) else prev) + v[i]) / n
        prev = out[i]
    return pd.Series(out, index=x.index)


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _vwma(x, v, n):
    s = v.rolling(n).sum()
    return (x * v).rolling(n).sum() / s.where(s != 0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    fast, slow = _vwma(o, v, int(p["fast"])), _vwma(o, v, int(p["slow"]))
    n, sm = int(p["filter_len"]), int(p["smooth"])
    up, dn = h.diff(), -lo.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).where(up.notna())
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trur = _wilder0(tr, n)
    plus, minus = _fixnan(100 * _wilder0(pdm, n) / trur), _fixnan(100 * _wilder0(mdm, n) / trur)
    s = plus + minus
    adx = (100 * _wilder0((plus - minus).abs() / s.where(s != 0, 1.0), sm)).to_numpy()
    src = (o + h + lo + c) / 4
    ch = src.diff()
    mu = (v * src.where(~(ch <= 0), 0.0)).rolling(n).sum()
    md = (v * src.where(~(ch >= 0), 0.0)).rolling(n).sum()
    mfi = (100.0 - 100.0 / (1.0 + mu / md.where(md != 0))).to_numpy()   # the formula only, as the source returns
    lc = ((fast > slow) & (fast.shift(1) <= slow.shift(1))).to_numpy()
    sc = ((fast < slow) & (fast.shift(1) >= slow.shift(1))).to_numpy()
    ov = o.to_numpy(dtype=float)
    k = int(p["knn"])
    k1, k2, kr = [0.0], [0.0], [0.0]
    prev1 = prev2 = prev_src = 0.0
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    for i in range(m):
        if lc[i] or sc[i]:
            k1.append(prev1)
            k2.append(prev2)
            kr.append(1.0 if ov[i] >= prev_src else -1.0)
            prev1, prev2, prev_src = adx[i], mfi[i], ov[i]
        if not (lc[i] or sc[i]):
            continue
        a1, a2, ar = np.array(k1), np.array(k2), np.array(kr)
        with np.errstate(invalid="ignore"):
            d = np.sqrt((adx[i] - a1) ** 2 + (mfi[i] - a2) ** 2)
        d = np.where(np.isnan(d), np.inf, d)
        kk = min(k, len(d))
        mth = np.partition(d, kk - 1)[kk - 1]
        vote = ar[d <= mth].sum() if np.isfinite(mth) else np.nan
        if lc[i] and vote >= 0:
            le[i] = True
        if sc[i] and vote < 0:
            se[i] = True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
