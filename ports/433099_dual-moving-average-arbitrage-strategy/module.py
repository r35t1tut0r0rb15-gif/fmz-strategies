"""HPotter combo, hourly bars: the 123-reversal state (stochastic 15 / 1 / 3 at 50) and the Finite Volume Elements state (a running sum of signed volume over its SMA 18, signed when the bar's money-flow move passes 0.6 % of the close, rising or falling against its last two values) both long goes long, both short goes short, any disagreement closes; reversing.
Port of FMZ strategy #433099 "Dual Moving Average Arbitrage Strategy" (Combo Backtest 123 Reversal & Finite Volume Elements (FVE)).

FMZ source id: 433099

Source
    https://www.fmz.com/strategy/433099 (PineScript v4, FMZ last modified 2023-11-24 14:21:06).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 156-201), 123 reversal: length 15, K smoothing 1, D length 3, level 50; FVE: period 18, factor 0.6; reverse off
    nMF = close - hl2 + hlc3 - hlc3[1];  nVlm = nMF > 0.6 % close ? volume : nMF < -0.6 % close ? -volume : 0;  nRes := nz(nRes[1]) + nVlm / sma(volume, 18) / 18 x 100
    posFVE = nRes above both previous values ? 1 : below both ? -1 : pos[1];  both 1 -> entry Long, both -1 -> entry Short, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The FVE volume enters only as a ratio to its own SMA 18, so its units do not matter. nRes starts at
      0 once the SMA exists (nz of its own history). reverse is off. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, combined price-pattern and volume-element states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the Finite Volume Elements sum (signed volume over its SMA 18); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433099_reversal123_finite_volume_elements_combo_reversal"
FAMILY = "hpotter_combo"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fve_period": [18, 30],
    "factor": [0.6, 0.3],
}
DEFAULT_PARAMS = {"length": 15, "k_smooth": 1, "d_len": 3, "level": 50.0, "fve_period": 18, "factor": 0.6}


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


def _reversal123(h, lo, c, length, k_smooth, d_len, level):
    """Pine's Reversal123 state: 1 / -1 on the pattern, else the last state (0 before any)."""
    with np.errstate(invalid="ignore", divide="ignore"):
        raw = 100 * (c - lo.rolling(length).min()) / (h.rolling(length).max() - lo.rolling(length).min())
    vf = raw.rolling(k_smooth).mean()
    vs = vf.rolling(d_len).mean()
    c1, c2 = c.shift(1), c.shift(2)
    up = ((c2 < c1) & (c > c1) & (vf < vs) & (vf > level)).to_numpy()
    dn = ((c2 > c1) & (c < c1) & (vf > vs) & (vf < level)).to_numpy()
    out = np.zeros(len(up), dtype=np.int8)
    q = 0
    for i in range(len(up)):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        out[i] = q
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    r123 = _reversal123(h, lo, c, int(p["length"]), int(p["k_smooth"]), int(p["d_len"]), float(p["level"]))
    n, f = int(p["fve_period"]), float(p["factor"])
    hlc3 = (h + lo + c) / 3
    nmf = c - (h + lo) / 2 + hlc3 - hlc3.shift(1)
    nvl = np.where(nmf > f * c / 100, v, np.where(nmf < -f * c / 100, -v, 0.0))
    smav = v.rolling(n).mean().to_numpy()
    with np.errstate(invalid="ignore", divide="ignore"):
        term = nvl / smav / n * 100
    m = len(term)
    res = np.full(m, np.nan)
    prev = np.nan
    for i in range(m):
        res[i] = (0.0 if np.isnan(prev) else prev) + term[i]
        prev = res[i]
    rs = pd.Series(res, index=c.index)
    r1, r2 = rs.shift(1), rs.shift(2)
    up = ((rs > r1) & (rs > r2)).to_numpy()
    dn = ((rs < r1) & (rs < r2)).to_numpy()
    pf = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        pf[i] = q
    sig = np.where((r123 == 1) & (pf == 1), 1, np.where((r123 == -1) & (pf == -1), -1, 0))
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if sig[i] == 1 and pos != 1:
            le[i], pos = True, 1
        elif sig[i] == -1 and pos != -1:
            se[i], pos = True, -1
        elif sig[i] == 0 and pos == 1:
            lx[i], pos = True, 0
        elif sig[i] == 0 and pos == -1:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
