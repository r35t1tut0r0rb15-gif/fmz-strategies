"""MP zero-lag EMA: the zero-lag EMA 8 crossing above the zero-lag EMA 21 goes long, crossing below
goes short (each reverses the other side); a close 3 % beyond the signal bar's close takes the profit.
Port of FMZ strategy #427369 "Zero-Lag EMA Trend Following Strategy".

FMZ source id: 427369

Source
    https://www.fmz.com/strategy/427369 (PineScript v3, FMZ last modified 2023-09-20 14:30:03).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 185-448), ZLEMA 8 / 21, pyramiding gate 1, TP 3 % on, SL and
trailing off
    zlema(x, n) = ema + (ema - ema(ema)); long = crossover(fast, slow); short = crossunder(fast, slow)
    longCondition = long while the long section count <= 1 (the first long after a short)
    reference = close of that signal bar; long_tp = close > reference x 1.03 and not longCondition
    entries on the conditions; close on long_tp / short_tp (mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The section counters (pyramiding gate 1) only let the first signal of a side count; the
      crosses alternate, so every cross counts. The take-profit reference is the signal bar's CLOSE,
      the test is on the completed bar's close (an exit signal, rule 3).
    * Trailing stop and stop loss are off by default (isTS / isSL false): not ported; the
      Fibonacci-band section after the orders only plots.
    * The 3 % take-profit is a fraction of price (kept as a percent).
    * strategy.entry reverses: REVERSAL INTENDED. The test window (2018 - year 77777777) is the
      author's backtest window: dropped.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and close-based exits.
    2 generic: PASS, MA lengths and a percent target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, commission stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427369_mp_zero_lag_ema"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 5],
    "slow": [21, 50],
    "tp_pct": [3.0, 1.5],
}
DEFAULT_PARAMS = {"fast": 8, "slow": 21, "tp_pct": 3.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _zlema(x, n):
    e1 = x.ewm(span=n, adjust=False).mean()
    return e1 + (e1 - e1.ewm(span=n, adjust=False).mean())


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
    f, s = _zlema(c, int(p["fast"])), _zlema(c, int(p["slow"]))
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    tp = p["tp_pct"] / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, ref = 0, np.nan
    for i in range(m):
        if up[i]:
            pos, ref = 1, cv[i]
        elif dn[i]:
            pos, ref = -1, cv[i]
        elif pos == 1 and cv[i] > ref * (1 + tp):
            pos = 0
        elif pos == -1 and cv[i] < ref * (1 - tp):
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
