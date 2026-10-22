"""Ehlers Cyber Cycle signal turns traded against the turn (opposite trade on), 1-hour bars: the smoothed cycle signal turning down goes long, turning up goes short; a position losing on the close more
than 8 bars after its last entry signal closes; reversing.
Port of FMZ strategy #442078 "Signal Smoothing Ehlers Cyber Cycle Strategy" (Ehlers Cyber Cycle Strategy).

FMZ source id: 442078

Source
    https://www.fmz.com/strategy/442078 (PineScript v3, FMZ last modified 2024-02-19 10:42:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 145-181), source hl2; alpha 0.07; lag 9; oppositeTrade on; pyramiding 1; 100 % of equity, commission 0.1
    cycle = na(cycle[7]) ? (src - 2 src[1] + src[2]) / 4 : (1 - a/2)^2 (smooth - 2 smooth[1] + smooth[2]) + 2 (1 - a) cycle[1] - (1 - a)^2 cycle[2];  signal = cycle / (lag + 1) + (1 - 1 / (lag + 1)) nz(signal[1])
    crossunder(signal, signal[1]) -> entry Long;  crossover(signal, signal[1]) -> entry Short  (oppositeTrade);  openprofit < 0 and barsSinceEntry > 8 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cycle recursion starts as written (the simple form while cycle[7] is na). openprofit < 0 is a
      sign-only test, ported as the close against the fill price (as #440336); barsSinceEntry counts
      bars since the last entry signal (reset while flat), as written. strategy.entry reverses: REVERSAL
      INTENDED. The 100 % of equity size and commission are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, cycle signal turns and a close-vs-fill loss test.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND439084 (2 members, best partner #439084, Jaccard 0.726); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442078_ehlers_cyber_cycle_turn_opposite_reversal"
FAMILY = "cycle_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "alpha": [0.07, 0.15],
    "lag": [9, 5],
}
DEFAULT_PARAMS = {"alpha": 0.07, "lag": 9, "loss_bars": 8, "opposite": True}


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


def _signal(bars_df, alpha, lag):
    src = ((bars_df["high"] + bars_df["low"]) / 2).to_numpy(dtype=float)
    m = len(src)
    sm = np.full(m, np.nan)
    for i in range(3, m):
        sm[i] = (src[i] + 2 * src[i - 1] + 2 * src[i - 2] + src[i - 3]) / 6
    cyc = np.full(m, np.nan)
    sig = np.full(m, np.nan)
    a2 = 1.0 / (lag + 1)
    prev = np.nan
    for i in range(m):
        if i < 7 or np.isnan(cyc[i - 7]):
            cyc[i] = (src[i] - 2 * src[i - 1] + src[i - 2]) / 4 if i >= 2 else np.nan
        else:
            cyc[i] = ((1 - 0.5 * alpha) ** 2 * (sm[i] - 2 * sm[i - 1] + sm[i - 2])
                      + 2 * (1 - alpha) * cyc[i - 1] - (1 - alpha) ** 2 * cyc[i - 2])
        prev = a2 * cyc[i] + (1 - a2) * (0.0 if np.isnan(prev) else prev)
        sig[i] = prev
    return sig


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    s = pd.Series(_signal(bars_df, float(p["alpha"]), int(p["lag"])), index=bars_df.index)
    s1, s2 = s.shift(1), s.shift(2)
    turn_dn = ((s < s1) & (s1 >= s2)).to_numpy()
    turn_up = ((s > s1) & (s1 <= s2)).to_numpy()
    if p["opposite"]:
        go_l, go_s = turn_dn, turn_up
    else:
        go_l, go_s = turn_up, turn_dn
    cv = bars_df["close"].to_numpy(dtype=float)
    ov = bars_df["open"].to_numpy(dtype=float)
    lb = int(p["loss_bars"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held, entry_i, bse = 0, -1, 0
    for i in range(m):
        bse += 1
        if held == 0:
            bse = 0
        new = held
        if go_l[i]:
            if new != 1:
                new = 1
            bse = 0
        if go_s[i]:
            if new != -1:
                new = -1
            bse = 0
        if held != 0 and new == held and bse > lb:
            fill = ov[entry_i]
            if (held == 1 and cv[i] < fill) or (held == -1 and cv[i] > fill):
                new, bse = 0, 0
        if new != held and new != 0:
            entry_i = i + 1
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
