"""Darvas box breakouts above the SMA 25, 1-hour bars, long only: a close crossing over the box top with the close over the SMA 25 buys; a close crossing under the box bottom sells.
Port of FMZ strategy #472252 "Dynamic Darvas Box Breakout with Moving Average Trend Confirmation Trading System" (DARVAS BOX with MA25 Buy Condition (AEG DARVAS)).

FMZ source id: 472252

Source
    https://www.fmz.com/strategy/472252 (PineScript v5, FMZ last modified 2024-11-18 16:02:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 125-175), box length 5; new high = high over the previous 5-bar high; top / bottom fixed 3 bars after a new high when the 3-bar high is under the 4-bar high; SMA 25
    NH = valuewhen(high > highest(high, 5)[1], high);  top / bottom = valuewhen(barssince(new high) == 3 and highest(high, 3) < highest(high, 4), NH / lowest(low, 5))
    crossover(close, top) and close > sma25 -> entry Buy;  crossunder(close, bottom) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The box values follow the source's valuewhen / barssince chain bar by bar (na until the first box).
      Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Darvas box breakouts with an SMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_472252_darvas_box_breakout_sma25_long"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "boxp": [5, 8],
    "ma_len": [25, 50],
}
DEFAULT_PARAMS = {"boxp": 5, "ma_len": 25}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["boxp"])
    ll = lo.rolling(n).min().to_numpy()
    k1, k2, k3 = h.rolling(n).max(), h.rolling(n - 1).max(), h.rolling(n - 2).max()
    newh = (h > k1.shift(1)).to_numpy()
    box1 = (k3 < k2).to_numpy()
    hv = h.to_numpy(dtype=float)
    m = len(hv)
    top, bot = np.full(m, np.nan), np.full(m, np.nan)
    nh, last_new, t, b = np.nan, None, np.nan, np.nan
    for i in range(m):
        if newh[i]:
            nh, last_new = hv[i], i
        if last_new is not None and i - last_new == n - 2 and box1[i]:
            t, b = nh, ll[i]
        top[i], bot[i] = t, b
    ts, bs = pd.Series(top, index=c.index), pd.Series(bot, index=c.index)
    ma = c.rolling(int(p["ma_len"])).mean()
    le = (c > ts) & (c.shift(1) <= ts.shift(1)) & (c > ma)
    lx = (c < bs) & (c.shift(1) >= bs.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
