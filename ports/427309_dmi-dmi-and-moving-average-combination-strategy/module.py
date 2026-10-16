"""Combo: 123 reversal and DMI + MA: long while both the 123-reversal state (stochastic 14 / 1 / 3,
level 50) and the DMI-MA state are long, short while both are short, flat otherwise. The DMI-MA state
turns long on a bar where +DI crosses above -DI AND the close crosses above SMA 30 (short mirrors).
Port of FMZ strategy #427309 "DMI and Moving Average Combination Strategy".

FMZ source id: 427309

Source
    https://www.fmz.com/strategy/427309 (PineScript v4, FMZ last modified 2023-09-19 21:51:14).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 180-237), 123: 14 / 1 / 3 / 50; MA 30, DMI 14, reverse off
    xPDI / xNDI = fixnan(100 rma(+DM / -DM, 14) / rma(tr, 14))
    pDM = PDI crosses above NDI (PDI > NDI and PDI[1] < NDI[1]) and close crosses above SMA 30 ? 1
        : the mirror ? -1 : pDM[1]
    both 1 -> long; both -1 -> short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md; as worker A's 123-reversal combos)
    * fFilter is defined but never used. Crosses use strict < / > on the previous bar, as written.
    * fixnan carries the last value forward in time (causal); tr is na on the first bar.
    * REVERSAL INTENDED; disagreement closes.
    * FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator and MA-cross states.
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

NAME = "fmz_427309_combo_123_dmi_ma"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_ma": [30, 60],
    "length_dmi": [14, 7],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "length_ma": 30, "length_dmi": 14}


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


def _fixnan(a):
    out = a.copy()
    last = np.nan
    for i in range(len(out)):
        if np.isnan(out[i]):
            out[i] = last
        else:
            last = out[i]
    return out


def _state(up, dn):
    out = np.zeros(len(up), dtype=np.int8)
    s = 0
    for i in range(len(up)):
        if up[i]:
            s = 1
        elif dn[i]:
            s = -1
        out[i] = s
    return out


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    st = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min())
    fast = st.rolling(int(p["k_smoothing"])).mean()
    slow = fast.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    lvl = p["level"]
    s123 = _state(((c2 < c1) & (c > c1) & (fast < slow) & (fast > lvl)).to_numpy(),
                  ((c2 > c1) & (c < c1) & (fast > slow) & (fast < lvl)).to_numpy())
    nd = int(p["length_dmi"])
    up, dn = h.diff(), -lo.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).where(up.notna())
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trur = _rma(tr, nd).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        pdi = _fixnan(np.where(trur == 0, np.nan, 100 * _rma(pdm, nd).to_numpy() / trur))
        ndi = _fixnan(np.where(trur == 0, np.nan, 100 * _rma(mdm, nd).to_numpy() / trur))
    pdi1 = np.concatenate(([np.nan], pdi[:-1]))
    ndi1 = np.concatenate(([np.nan], ndi[:-1]))
    ma = c.rolling(int(p["length_ma"])).mean().to_numpy()
    ma1 = np.concatenate(([np.nan], ma[:-1]))
    cv = c.to_numpy(dtype=float)
    cv1 = np.concatenate(([np.nan], cv[:-1]))
    di_up, di_dn = (pdi > ndi) & (pdi1 < ndi1), (pdi < ndi) & (pdi1 > ndi1)
    ma_up, ma_dn = (cv > ma) & (cv1 < ma1), (cv < ma) & (cv1 > ma1)
    sdm = _state(di_up & ma_up, di_dn & ma_dn)
    tgt = np.where((s123 == 1) & (sdm == 1), 1, np.where((s123 == -1) & (sdm == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
