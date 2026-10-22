"""G-Channel trend flips (length 100), no bar size in the source: the trend turning bullish (the close last broke the upper extremity more recently than the lower) goes long, turning bearish goes short; reversing. The bracket re-sent every bar from the current close is not ported (pending).
Port of FMZ strategy #452822 "G-Channel-Trend-Detection-Strategy-G-Channel趋势检测策略" (G-Channel Trend Detection Strategy (G-Trend)).

FMZ source id: 452822

Source
    https://www.fmz.com/strategy/452822 (PineScript v5, FMZ last modified 2024-05-29 17:06:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 79-141), G-Channel length 100; take profit 5 %, stop 2 % of the current close (re-sent every bar)
    a = max(close, a[1]) - (a[1] - b[1]) / 100;  b = min(close, b[1]) + (a[1] - b[1]) / 100
    bullish = barssince(crossunder(a, close)) <= barssince(crossunder(b, close));  turns bullish -> entry Buy;  turns bearish -> entry Sell
    every bar: exit(Buy, limit = close x 1.05, stop = close x 0.98);  exit(Sell, limit = close x 0.95, stop = close x 1.02)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel starts from 0 (nz) as written. barssince is na until its event has happened, and a
      comparison with na is false, so the trend reads bearish until both events exist. The bracket
      is re-sent on every bar from that bar's close, so its levels move with the price; stops()
      cannot express this: it is not ported and the module gets the mark trailing_stop_pending (as
      #438034); positions end at the opposite entry. The source has no backtest header and names no
      bar size: FREQ = "bar_size_pending" (rule 1); precompute builds the bars with the house
      bar_sizes.build_bars with the driver's bar_size. REVERSAL INTENDED. No sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the per-bar bracket pending (mark).
    2 generic: PASS, G-Channel trend flips.
    3 crypto-exchange-only: no (no exchange named).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_452822_g_channel_trend_flip_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50],
}
DEFAULT_PARAMS = {"length": 100}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def _barssince(ev):
    out = np.full(len(ev), np.nan)
    last = -1
    for i in range(len(ev)):
        if ev[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = float(p["length"])
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    a, b = np.full(m, np.nan), np.full(m, np.nan)
    pa = pb = 0.0
    for i in range(m):
        a[i] = max(cv[i], pa) - (pa - pb) / n
        b[i] = min(cv[i], pb) + (pa - pb) / n
        pa, pb = a[i], b[i]
    sa, sb = pd.Series(a, index=c.index), pd.Series(b, index=c.index)
    c1 = c.shift(1)
    cross_up = ((sb < c) & (sb.shift(1) >= c1)).to_numpy()     # crossunder(b, close)
    cross_dn = ((sa < c) & (sa.shift(1) >= c1)).to_numpy()     # crossunder(a, close)
    bu, bd = _barssince(cross_up), _barssince(cross_dn)
    with np.errstate(invalid="ignore"):
        bull = pd.Series(bd <= bu, index=c.index)
    prev = bull.shift(1, fill_value=False)
    le = bull & ~prev
    se = ~bull & prev
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
