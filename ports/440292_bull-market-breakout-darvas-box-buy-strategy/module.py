"""Darvas box breakouts, 1-hour bars, long only: when a new 5-bar high is followed by three bars that confirm a box, its top and bottom are kept; the close crossing over the box top goes long from flat, with a
stop at the box bottom and a target at five times the box bottom.
Port of FMZ strategy #440292 "Bull Market Breakout Darvas Box Buy Strategy" (Darvas Box Strategy - Buy Only).

FMZ source id: 440292

Source
    https://www.fmz.com/strategy/440292 (PineScript v4, FMZ last modified 2024-01-29 09:53:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 167-212), box length 5; target = 5 x stop level
    LL = lowest(low, 5);  k1 = highest(high, 5), k2 = highest(high, 4), k3 = highest(high, 3);  NH = valuewhen(high > k1[1], high, 0);  box1 = k3 < k2
    TopBox / BottomBox = valuewhen(barssince(high > k1[1]) == 3 and box1, NH / LL, 0);  crossover(close, TopBox) -> entry Buy;  every bar: strategy.exit(stop = BottomBox, limit = 5 BottomBox)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop and target are re-sent every bar at the current box bottom, which moves when a new box
      forms. The port takes them from the signal bar: sl_stop = (close - BottomBox) / close and tp_stop =
      5 BottomBox / close - 1, shifted one bar inside stops() and re-based on the fill (a bottom at or
      above the close places no trade); the later moves are not followed: mark trailing_stop_pending. The
      target five times the bottom is out of reach in practice, as written. An entry while long is
      ignored (one position), so trades start only from flat. Long only. Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving box bottom pending.
    2 generic: PASS, box levels from past highs and lows.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_440292_darvas_box_breakout_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "box_len": [5, 10],
}
DEFAULT_PARAMS = {"box_len": 5, "tp_mult": 5.0}


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


def _fixnan(x):
    """Pine fixnan / valuewhen(..., 0): the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _barssince(cond):
    v = cond.to_numpy(dtype=bool)
    out = np.full(len(v), np.nan)
    last = -1
    for i in range(len(v)):
        if v[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["box_len"])
    ll = lo.rolling(n).min()
    k1, k2, k3 = h.rolling(n).max(), h.rolling(n - 1).max(), h.rolling(n - 2).max()
    newhigh = h > k1.shift(1)
    nh = _fixnan(h.where(newhigh))
    cond = (_barssince(newhigh) == n - 2) & (k3 < k2).to_numpy()
    top = _fixnan(nh.where(cond))
    bot = _fixnan(ll.where(cond))
    enter = (c > top) & (c.shift(1) <= top.shift(1))
    sl = ((c - bot) / c).where(enter)
    tp = (float(p["tp_mult"]) * bot / c - 1).where(enter)
    ok = (sl > 0) & (tp > 0)
    return sl.where(ok), tp.where(ok)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_s, tp_s = _setup(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos == 1 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_):
                pos = 0
        if pos == 0 and i + 1 < m and not np.isnan(sl[i]):
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
