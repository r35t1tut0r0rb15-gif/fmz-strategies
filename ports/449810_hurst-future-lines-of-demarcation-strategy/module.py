"""Hurst FLD states from ohlc4 shifted 3, 10 and 40 bars, 10-minute bars: in state A (signal > trade > trend) a price crossing over the signal FLD goes long, in state F a price crossing under it goes
short; the price crossing back under (over) the trade FLD closes; reversing.
Port of FMZ strategy #449810 "Hurst Future Lines of Demarcation Strategy" (Hurst Future Lines of Demarcation Strategy).

FMZ source id: 449810

Source
    https://www.fmz.com/strategy/449810 (PineScript v5, FMZ last modified 2024-04-29 13:58:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-219), source ohlc4; FLD smoothing off; cycles 5 / 20 / 80 (shifts 3 / 10 / 40); close triggers Price vs Trade
    signal = src[3], trade = src[10], trend = src[40];  state A..H from their order and price < signal;  buy = crossover(price, signal) and state == 1;  sell = crossunder(price, signal) and state == 6
    close_buy = long and crossunder(price, trade);  close_sell = short and crossover(price, trade)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With smoothing off the FLD is the source itself; the shifts are math.round(cycle / 2), so 5 / 2
      rounds to 3. The state machine runs its eight tests in order each bar, as written. Calls run in
      order: a close acts only on a position held into the bar and not reversed by that bar's entry.
      REVERSAL INTENDED. No sizing code. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the FLDs are past values.
    2 generic: PASS, FLD state machine crossings.
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
import math

import numpy as np
import pandas as pd

NAME = "fmz_449810_hurst_fld_state_cross_reversal"
FAMILY = "cycle_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cyc_q": [5, 10],
    "cyc": [20, 40],
}
DEFAULT_PARAMS = {"cyc_q": 5, "cyc": 20, "cyc_d": 80}


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


def _half(n):
    return int(math.floor(n / 2 + 0.5))              # math.round: halves round up


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    src = (bars_df["open"] + bars_df["high"] + bars_df["low"] + bars_df["close"]) / 4
    sig = src.shift(_half(int(p["cyc_q"])))
    trd = src.shift(_half(int(p["cyc"])))
    tnd = src.shift(_half(int(p["cyc_d"])))
    pv, sv, tv, nv = (x.to_numpy(dtype=float) for x in (src, sig, trd, tnd))
    m = len(pv)
    state = np.zeros(m)
    st = 0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if sv[i] > tv[i] and tv[i] > nv[i]:
                st = 1
            if st == 1 and pv[i] < sv[i]:
                st = 2
            if sv[i] < tv[i] and tv[i] > nv[i]:
                st = 3
            if st == 3 and pv[i] < sv[i]:
                st = 4
            if sv[i] < tv[i] and tv[i] < nv[i]:
                st = 5
            if st == 5 and pv[i] < sv[i]:
                st = 6
            if sv[i] > tv[i] and tv[i] < nv[i]:
                st = 7
            if st == 7 and pv[i] < sv[i]:
                st = 8
            state[i] = st
        p1 = np.concatenate(([np.nan], pv[:-1]))
        s1 = np.concatenate(([np.nan], sv[:-1]))
        t1 = np.concatenate(([np.nan], tv[:-1]))
        buy = (pv > sv) & (p1 <= s1) & (state == 1)
        sell = (pv < sv) & (p1 >= s1) & (state == 6)
        xb = (pv < tv) & (p1 >= t1)
        xs = (pv > tv) & (p1 <= t1)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            le[i], new = True, 1
        if xb[i] and pos == 1 and new == 1:          # close_buy reads the held position
            lx[i], new = True, 0
        if sell[i] and new != -1:
            se[i], le[i], lx[i], new = True, False, False, -1
        if xs[i] and pos == -1 and new == -1:
            sx[i], new = True, 0
        pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
