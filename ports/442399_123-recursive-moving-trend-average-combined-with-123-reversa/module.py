"""HPotter combo of the 123 reversal and the Recursive Moving Trend Average (21), 1-hour bars: long when the 123 state is long and the RMTA is under the previous close, short on the mirror, flat otherwise;
reversing.
Port of FMZ strategy #442399 "递归移动趋势均线结合123形态反转的组合策略Recursive-Moving-Trend-Average-Combined-with-123-Reversal-Pattern-Strategy" (Combo Backtest 123 Reversal & Recursive Moving Trend Average).

FMZ source id: 442399

Source
    https://www.fmz.com/strategy/442399 (PineScript v4, FMZ last modified 2024-02-21 16:02:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-165), 123: stochastic 14, K smoothing 1, D 3, level 50; RMTA 21; reverse off
    123: close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50 -> 1;  mirrored -> -1;  else previous
    RMTA: Bot = (1 - a) nz(Bot[1], close) + close;  nRes = (1 - a) nz(nRes[1], close) + a (close + Bot - nz(Bot[1], 0)), a = 2 / 22;  nRes > close[1] -> -1, < -> 1, else previous

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both states are ported as written (the RMTA's nz starts). The combined state is a level;
      disagreement closes. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close pattern, stochastic and RMTA states.
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

NAME = "fmz_442399_reversal123_rmta_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_rmta": [21, 10],
}
DEFAULT_PARAMS = {"length": 14, "length_rmta": 21, "k_smoothing": 1, "d_length": 3, "level": 50.0, "reverse": False}


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
    a = 2.0 / (int(p["length_rmta"]) + 1)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = pr = 0
    bot = res = np.nan
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        bot_prev = bot
        bot = (1 - a) * (cv[i] if np.isnan(bot_prev) else bot_prev) + cv[i]
        res = (1 - a) * (cv[i] if np.isnan(res) else res) + a * (cv[i] + bot - (0.0 if np.isnan(bot_prev) else bot_prev))
        if i > 0:
            if res > cv[i - 1]:
                pr = -1
            elif res < cv[i - 1]:
                pr = 1
        tgt[i] = 1 if (p123 == 1 and pr == 1) else (-1 if (p123 == -1 and pr == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
