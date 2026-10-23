"""HPotter combo, 15-minute bars: the 123-reversal state (stochastic 14 / 1 / 3 at 50) and the modified price-volume-trend state (the cumulative volume-weighted ohlc4 return above / below its SMA 23) both long goes long, both short goes short, any disagreement closes; reversing.
Port of FMZ strategy #439980 "Combo Strategy of Double Factors Reversal and Improved Price Volume Trend" (Combo Backtest 123 Reversal & Modified Price-Volume Trend (HPotter)).

FMZ source id: 439980

Source
    https://www.fmz.com/strategy/439980 (PineScript v4, FMZ last modified 2024-01-25 14:46:36).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 128-173), 123 reversal: length 14, K smoothing 1, D length 3, level 50; MPVT level 1, scale 1, length 23; reverse off
    xCumPVT := nz(xCumPVT[1]) + volume / 50000 * (ohlc4 - ohlc4[1]) / ohlc4[1];  nRes = 1 + 1 * xCumPVT;  posMPVT = nRes > sma(nRes, 23) ? 1 : nRes < sma ? -1 : pos[1]
    pos = both 1 ? 1 : both -1 ? -1 : 0;  1 -> entry Long, -1 -> entry Short, 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volume / 50000 scale and the level 1 cancel in the comparison with the SMA (a positive scale
      and an offset do not change which side of its average the line is on), so the port compares the
      plain cumulative sum. The first bar's na return adds nothing. reverse is off. REVERSAL INTENDED. No
      sizing code. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, combined price-pattern and price-volume-trend states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the weight of each ohlc4 return in the cumulative price-volume trend; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439980_reversal123_modified_pvt_combo_15m_reversal"
FAMILY = "hpotter_combo"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "pvt_len": [23, 50],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_len": 3, "level": 50.0, "pvt_len": 23}


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
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    r123 = _reversal123(h, lo, c, int(p["length"]), int(p["k_smooth"]), int(p["d_len"]), float(p["level"]))
    x = (o + h + lo + c) / 4
    pvt = (v * (x - x.shift(1)) / x.shift(1)).fillna(0.0).cumsum()
    ma = pvt.rolling(int(p["pvt_len"])).mean()
    raw = np.where(pvt > ma, 1, np.where(pvt < ma, -1, 0))
    m = len(raw)
    pv = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if raw[i] != 0:
            q = raw[i]
        pv[i] = q
    s = np.where((r123 == 1) & (pv == 1), 1, np.where((r123 == -1) & (pv == -1), -1, 0))
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if s[i] == 1 and pos != 1:
            le[i], pos = True, 1
        elif s[i] == -1 and pos != -1:
            se[i], pos = True, -1
        elif s[i] == 0 and pos == 1:
            lx[i], pos = True, 0
        elif s[i] == 0 and pos == -1:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
