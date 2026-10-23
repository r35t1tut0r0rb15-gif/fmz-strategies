"""HPotter combo, hourly bars: the 123-reversal state (stochastic 14 / 1 / 3 at 50) and the volume-weighted EMA 22 state (VWEMA under the previous close = 1, over = -1) both long goes long, both short goes short, any disagreement closes; reversing.
Port of FMZ strategy #434579 "双重优化组合反转EMA加权交易策略Comb-Reverse-EMA-Volume-Weighting-Optimization-Trading-Strategies" (Combo Backtest 123 Reversal & EMA & Volume Weighting (HPotter)).

FMZ source id: 434579

Source
    https://www.fmz.com/strategy/434579 (PineScript v4, FMZ last modified 2023-12-07 16:39:50).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 154-193), 123 reversal: length 14, K smoothing 1, D length 3, level 50; EMA_VW length 22; reverse off
    nRes = ema(volume x close, 22) / ema(volume, 22);  posEMA_VW = nRes < close[1] ? 1 : nRes > close[1] ? -1 : pos[1]
    pos = both 1 ? 1 : both -1 ? -1 : 0;  1 -> entry Long, -1 -> entry Short, 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The VWEMA is a ratio of two volume EMAs, so the volume's units cancel. fFilter is defined but never
      called. reverse is off. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, combined price-pattern and volume-weighted EMA states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the volume-weighted EMA 22; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434579_reversal123_vwema22_combo_reversal"
FAMILY = "hpotter_combo"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_vw": [22, 50],
    "length": [14, 9],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_len": 3, "level": 50.0, "length_vw": 22}


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
    n = int(p["length_vw"])
    ev = v.ewm(span=n, adjust=False).mean()
    nres = (v * c).ewm(span=n, adjust=False).mean() / ev.where(ev != 0)
    c1 = c.shift(1)
    raw = np.where(nres < c1, 1, np.where(nres > c1, -1, 0))
    pv = np.zeros(len(raw), dtype=np.int8)
    q = 0
    for i in range(len(raw)):
        if raw[i] != 0:
            q = raw[i]
        pv[i] = q
    sig = np.where((r123 == 1) & (pv == 1), 1, np.where((r123 == -1) & (pv == -1), -1, 0))
    m = len(sig)
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
