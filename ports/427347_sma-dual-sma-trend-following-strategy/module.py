"""Noro's Trend SMA v1.4: a trend state from the mid-channel of ohlc4 (20 bars), up when a whole bar
(its low) is above the centre, down when a whole bar (its high) is below it; in an up-trend a dip
under the fast EMA 5 on two red bars goes long, in a down-trend a pop above it on two green bars goes
short (always in the market after the first entry).
Port of FMZ strategy #427347 "Dual SMA Trend Following Strategy".

FMZ source id: 427347

Source
    https://www.fmz.com/strategy/427347 (PineScript v2, FMZ last modified 2023-09-20 11:35:30).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 125-162), fast 5, slow 20, bars 2, fast filter on
    center = (highest(ohlc4, 20) + lowest(ohlc4, 20)) / 2
    trend = low > center ? 1 : high < center ? -1 : trend[1]
    up = trend 1 and low < ema(close, 5) and two red bars -> entry long
    dn = trend -1 and high > ema(close, 5) and two green bars -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "fast SMA" / "slow SMA" are EMAs in the code (only the fast one is used); the channel uses
      the slow length. As in worker A's / FMZ-C's other Noro trend ports.
    * strategy.entry reverses: REVERSAL INTENDED (no other exit).
    * FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths and bar counts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427347_noro_trend_sma_v14"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow_len": [20, 10, 40],
    "bars": [2, 1],
}
DEFAULT_PARAMS = {"fast_len": 5, "slow_len": 20, "bars": 2, "use_fast": True}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["slow_len"])
    src = (o + h + lo + c) / 4
    center = ((src.rolling(n).max() + src.rolling(n).min()) / 2).to_numpy()
    fast = c.ewm(span=int(p["fast_len"]), adjust=False).mean().to_numpy()
    bar = np.sign(c - o).to_numpy()
    nb = int(p["bars"])
    red = np.ones(len(bar), dtype=bool)
    green = np.ones(len(bar), dtype=bool)
    for k in range(nb):
        bk = np.concatenate((np.zeros(k), bar[:len(bar) - k])) if k else bar
        red &= bk == -1
        green &= bk == 1
    use_fast = bool(p["use_fast"])
    lv, hv = lo.to_numpy(dtype=float), h.to_numpy(dtype=float)
    m = len(bar)
    tgt = np.zeros(m, dtype=np.int8)
    trend, pos = 0, 0
    for i in range(m):
        if lv[i] > center[i]:
            trend = 1
        elif hv[i] < center[i]:
            trend = -1
        if trend == 1 and (lv[i] < fast[i] or not use_fast) and red[i] and pos != 1:
            pos = 1
        elif trend == -1 and (hv[i] > fast[i] or not use_fast) and green[i] and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
