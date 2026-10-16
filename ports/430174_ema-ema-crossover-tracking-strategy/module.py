"""Supertrend (close-based, ATR 11 x 3) with an EMA 20 / 50 filter, 1-hour bars: an up-trend with EMA 20 at or above EMA 50
goes long, a down-trend with EMA 20 at or below EMA 50 goes short; a trend flip closes the position (and enters the
other side when its EMA condition holds).
Port of FMZ strategy #430174 "EMA交叉追踪策略EMA-Crossover-tracking-Strategy" (Ema Crossover).

FMZ source id: 430174

Source
    https://www.fmz.com/strategy/430174 (PineScript v5, FMZ last modified 2023-10-25 17:44:35).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 210-263), ATR 11 (Wilder), multiplier 3, EMA 20 / 50, both sides on
    up = close - 3 atr, ratcheted while close[1] > up[1]; dn = close + 3 atr, ratcheted while close[1] < dn[1]
    trend flips to 1 when close > dn[1], to -1 when close < up[1]
    ema20 >= ema50 and trend == 1 -> entry long; long and trend == -1 -> close long
    ema20 <= ema50 and trend == -1 -> entry short; short and trend == 1 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bands are built from the close (not hl2), as written. "Change ATR method" is on: Wilder ATR.
    * A long whose trend flips is closed; when the EMA condition of the short side also holds on that
      bar the short entry reverses it instead.
    * The 2021-01-01 to 2023-10-30 window is the author's backtest window: dropped.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bands and moving averages.
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

NAME = "fmz_430174_close_supertrend_ema_filter"
FAMILY = "supertrend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "periods": [11, 20],
    "multiplier": [3.0, 2.0],
}
DEFAULT_PARAMS = {"periods": 11, "multiplier": 3.0, "fast": 20, "slow": 50}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


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
    c = bars_df["close"]
    atr = _atr(bars_df, int(p["periods"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    mult = float(p["multiplier"])
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    lc, sc = (ef >= es).to_numpy(), (ef <= es).to_numpy()
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    up_prev = dn_prev = np.nan
    trend, pos = 1, 0
    for i in range(m):
        up, dn = cv[i] - mult * atr[i], cv[i] + mult * atr[i]
        up1 = up if np.isnan(up_prev) else up_prev
        dn1 = dn if np.isnan(dn_prev) else dn_prev
        if i > 0 and cv[i - 1] > up1:
            up = max(up, up1)
        if i > 0 and cv[i - 1] < dn1:
            dn = min(dn, dn1)
        if trend == -1 and cv[i] > dn1:
            trend = 1
        elif trend == 1 and cv[i] < up1:
            trend = -1
        up_prev, dn_prev = up, dn
        start = pos
        if lc[i] and trend == 1:
            pos = 1
        if start == 1 and trend == -1:
            pos = 0
        if sc[i] and trend == -1:
            pos = -1
        if start == -1 and trend == 1 and pos == -1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
