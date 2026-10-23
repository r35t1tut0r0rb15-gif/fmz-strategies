"""Hourly bars, long only: a confirmed 5-bar bottom fractal on a bar that opens at least 0.01 % under the latest volume-confirmed down-fractal level goes long; a confirmed top fractal on a bar that opens above the latest volume-confirmed up-fractal level closes.
Port of FMZ strategy #434177 "Adaptive Volatility Breakout Trading Strategy" (TradingGroundhog - Strategy & Fractal V1 - Short term).

FMZ source id: 434177

Source
    https://www.fmz.com/strategy/434177 (PineScript v4, FMZ last modified 2023-12-04 14:34:13).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 122-261), Bill Williams filter on, extreme filter on (window 2); volume MA 2; long stop loss 0.01 % (entry gap only); start 2021-09-13
    fractaldown := low[3] < low[4] < low[5] and low[2] > low[3] and low[1] > low[2] and volume[3] > sma(volume, 2)[3] ? low[3] : fractaldown[1];  Bottom_1 = fractaldown (the newest saved value)
    filteredbotf and open < Bottom_1 and (Bottom_1 - open) / Bottom_1 >= 0.0001 -> entry Long;  filteredtopf and open > Top_1 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * With "filter Bill Williams Fractals" on, the fractals are the regular strict 5-bar pattern (centre 2
      bars back); the extreme filter (window 2) is then always met. The save loops put the current
      fractal level first, so Bottom_1 / Top_1 are the current fractaldown / fractalup; the older saved
      levels feed nothing. Signal_Test_TEMP is set and cleared on the same bar, so the exit is "a top
      fractal on a bar opening above Top_1". volume[3] > sma(volume, 2)[3] compares the bar with the one
      before it. "Long Stop Loss (%)" only sizes the entry gap test; no stop order. The 2021-09-13 start is
      dropped. A close acts only on a position the bar's entries leave unchanged (call order). Long only.
      The 10000 cash per lot is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, fractal reversal entries under the last volume fractal level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = 10000 cash per lot, pyramiding 1, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the fractal levels' test volume[3] > sma(volume, 2)[3]; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the author's 2021-09-13 start dropped).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434177_fractal_bottom_gap_under_volume_fractal_level_long"
FAMILY = "fractal"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "gap_pct": [0.0001, 0.002],
    "vol_ma": [2, 5],
}
DEFAULT_PARAMS = {"gap_pct": 0.0001, "vol_ma": 2}


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


def _hold(cond, val):
    """x := cond ? val : x[1] (NaN before the first)."""
    c, v = np.asarray(cond, dtype=bool), np.asarray(val, dtype=float)
    out = np.full(len(c), np.nan)
    q = np.nan
    for i in range(len(c)):
        if c[i]:
            q = v[i]
        out[i] = q
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, v = (bars_df[k] for k in ("open", "high", "low", "volume"))
    hs = [h.shift(k) for k in range(6)]
    ls = [lo.shift(k) for k in range(6)]
    topf = (hs[4] < hs[3]) & (hs[3] < hs[2]) & (hs[2] > hs[1]) & (hs[1] > hs[0])
    botf = (ls[4] > ls[3]) & (ls[3] > ls[2]) & (ls[2] < ls[1]) & (ls[1] < ls[0])
    vam = v.rolling(int(p["vol_ma"])).mean()
    vok = v.shift(3) > vam.shift(3)
    up = (hs[3] > hs[4]) & (hs[4] > hs[5]) & (hs[2] < hs[3]) & (hs[1] < hs[2]) & vok
    dn = (ls[3] < ls[4]) & (ls[4] < ls[5]) & (ls[2] > ls[3]) & (ls[1] > ls[2]) & vok
    top1 = _hold(up.to_numpy(), hs[3].to_numpy())
    bot1 = _hold(dn.to_numpy(), ls[3].to_numpy())
    ov = o.to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        ent = botf.to_numpy() & (ov < bot1) & ((bot1 - ov) / bot1 >= float(p["gap_pct"]))
        ext = topf.to_numpy() & (ov > top1)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and ent[i]:
            le[i], pos = True, 1
        elif pos == 1 and ext[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
