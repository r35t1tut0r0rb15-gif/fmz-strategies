"""Lucid SAR flips, 15-minute bars: a SAR flip bar (either direction) sends the short entry, which wins on that bar; every other bar of an up trend sends the long entry; so a down flip goes short and an up flip
goes long one bar later, as written; reversing.
Port of FMZ strategy #439962 "Intelligent Trailing Stop Loss Strategy" (Lucid SAR Strategy).

FMZ source id: 439962

Source
    https://www.fmz.com/strategy/439962 (PineScript v4, FMZ last modified 2024-01-25 12:50:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 142-244), AF initial 0.02, increment 0.02, maximum 0.2
    Lucid SAR: EP / AF / SAR recursion from the previous bar, flips when the SAR crosses the bar (newtrend true on the flip bar, both directions)
    if uptrend: entry PBSARLE (long);  if newtrend: entry PBSARSE (short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Inside the recursion "if newtrend" reads the current bar's newtrend before it is set, which is
      always false there, as written. newtrend is true on both kinds of flip, so an up-flip bar sends
      both entries and the later short wins (as #437773); the long follows on the next bar of the up
      trend (the intended short-on-down-flip-only version is owed). strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SAR recursion.
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

NAME = "fmz_439962_lucid_sar_flip_as_written"
FAMILY = "parabolic_sar"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "af_increment": [0.02, 0.01],
    "af_maximum": [0.2, 0.1],
}
DEFAULT_PARAMS = {"af_increment": 0.02, "af_maximum": 0.2, "af_initial": 0.02}


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
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    a0, inc, amax = float(p["af_initial"]), float(p["af_increment"]), float(p["af_maximum"])
    m = len(hv)
    up = np.ones(m, dtype=bool)
    nt = np.zeros(m, dtype=bool)
    ep, sar, af = hv.copy(), lv.copy(), np.full(m, a0)
    for i in range(1, m):
        u1, n1, ep1, s1, a1 = up[i - 1], nt[i - 1], ep[i - 1], sar[i - 1], af[i - 1]
        e = max(hv[i], ep1) if u1 else min(lv[i], ep1)
        if n1:
            a = a0
        else:
            a = min(amax, a1 + inc) if e != ep1 else a1
        s = s1 + a * (e - s1)
        u, n = True, False
        if u1:
            s = min(s, lv[i - 1])
            if i >= 2:
                s = min(s, lv[i - 2])
            if s > lv[i]:
                u, n = False, True
                s = max(hv[i], ep1)
                e = min(lv[i], lv[i - 1])
        else:
            s = max(s, hv[i - 1])
            if i >= 2:
                s = max(s, hv[i - 2])
            if s < hv[i]:
                u, n = True, True
                s = min(lv[i], ep1)
                e = max(hv[i], hv[i - 1])
            else:
                u, n = False, False
        up[i], nt[i], ep[i], sar[i], af[i] = u, n, e, s, a
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if nt[i]:
            pos = -1
        elif up[i]:
            pos = 1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
