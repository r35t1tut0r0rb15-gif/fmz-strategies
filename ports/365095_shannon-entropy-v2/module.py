"""A Shannon-entropy line of log volume minus the close (9 bars), 2-hour bars: its 44-bar percent rank under 2 goes long, otherwise over 98 goes short; reversing.
Port of FMZ strategy #365095 "Shannon Entropy V2" (Shannon Entropy V2).

FMZ source id: 365095

Source
    https://www.fmz.com/strategy/365095 (PineScript v4, FMZ last modified 2022-05-24 10:13:21).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 56-105), entropy length 9; averaging 44; percent rank limit 2; source and volume both included
    cr = close / sum(close, 9);  vr = log(volume) / sum(log(volume), 9);  info = sum(vr log2 vr, 9) - sum(cr log2 cr, 9)
    percentrank(info, 44) < 2 -> entry Long;  else > 98 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A study() script sending strategy orders on FMZ. percentrank is Pine's: the share of the previous
      44 values at or under the current one. A bar of zero volume has an undefined log and leaves the
      line na around it, as written. The WMA / stdev bands are display only. REVERSAL INTENDED. No sizing
      code. The source carries the Mozilla Public License 2.0 notice. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, entropy percent-rank extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as log(volume) shares in the entropy line; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365095_shannon_entropy_close_log_volume_pctrank_extreme_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [9, 20],
    "avg": [44, 100],
}
DEFAULT_PARAMS = {"len": 9, "avg": 44, "vpr": 2}


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


def _percentrank(x, n):
    """Pine percentrank: % of the previous n values that are <= the current one."""
    v = x.to_numpy(dtype=float)
    m = len(v)
    out = np.full(m, np.nan)
    if m > n:
        win = np.lib.stride_tricks.sliding_window_view(v, n + 1)   # columns: t-n .. t
        cur = win[:, -1:]
        prev = win[:, :-1]
        ok = ~np.isnan(win).any(axis=1)
        out[n:] = np.where(ok, (prev <= cur).sum(axis=1) / n * 100, np.nan)
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    n = int(p["len"])
    with np.errstate(divide="ignore", invalid="ignore"):
        lv = np.log(v.where(v > 0))
        cr = c / c.rolling(n).sum()
        vr = lv / lv.rolling(n).sum()
        info = (vr * np.log2(vr)).rolling(n).sum() - (cr * np.log2(cr)).rolling(n).sum()
    hvp = _percentrank(info, int(p["avg"]))
    lim = float(p["vpr"])
    le = hvp < lim
    se = (hvp > 100 - lim) & ~le
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
