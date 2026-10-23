"""HPotter combo, one-minute bars: the 123-reversal state (stochastic 14 / 1 / 3 at 50) and the Negative Volume Index state (a running sum of the 50-bar rate of change on bars whose volume fell, against its EMA 50) both long goes long, both short goes short, any disagreement closes; reversing.
Port of FMZ strategy #436645 "Quantitative Reversal Index Strategy Integrating Dual Trend Signals" (Combo Backtest 123 Negative Volume Index (HPotter)).

FMZ source id: 436645

Source
    https://www.fmz.com/strategy/436645 (PineScript v4, FMZ last modified 2023-12-26 15:47:36).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 159-199), 123 reversal: length 14, K smoothing 1, D length 3, level 50; NVI EMA 50; reverse off
    nRes := volume < volume[1] ? nz(nRes[1]) + roc(close, 50) : nz(nRes[1]);  posNVI = nRes > ema(nRes, 50) ? 1 : nRes < ema ? -1 : pos[1]
    pos = both 1 ? 1 : both -1 ? -1 : 0;  1 -> entry Long, -1 -> entry Short, 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The NVI only compares each bar's volume with the previous one. The running sum starts at 0 (nz).
      reverse is off. REVERSAL INTENDED. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, combined price-pattern and negative-volume-index states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the Negative Volume Index test volume < volume[1]; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436645_reversal123_negative_volume_index_combo_1m_reversal"
FAMILY = "hpotter_combo"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [50, 100],
    "length": [14, 9],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_len": 3, "level": 50.0, "ema_len": 50}


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
    n = int(p["ema_len"])
    roc = (100 * (c - c.shift(n)) / c.shift(n)).to_numpy()
    vdown = (v < v.shift(1)).to_numpy()
    m = len(roc)
    res = np.zeros(m)
    prev = 0.0
    for i in range(m):
        cur = prev + roc[i] if vdown[i] else prev
        res[i] = cur
        prev = 0.0 if np.isnan(cur) else cur
    rs = pd.Series(res, index=c.index)
    e = rs.ewm(span=n, adjust=False).mean()
    raw = np.where(rs > e, 1, np.where(rs < e, -1, 0))
    pv = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if raw[i] != 0:
            q = raw[i]
        pv[i] = q
    sig = np.where((r123 == 1) & (pv == 1), 1, np.where((r123 == -1) & (pv == -1), -1, 0))
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
