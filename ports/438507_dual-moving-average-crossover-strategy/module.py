"""A one-way short, 1-minute bars: the "previous" EMA state is computed from a zero seed and is always 1, so the cross test never returns 1 and the script sends a Short entry on every bar; the first short is
held to the end of the data.
Port of FMZ strategy #438507 "Dual Moving Average Crossover Strategy" (ParkerMAStrat).

FMZ source id: 438507

Source
    https://www.fmz.com/strategy/438507 (PineScript v2, FMZ last modified 2024-01-12 14:59:18).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 176-290), EMA lengths 30 / 60 (zero-seeded hand-written EMAs)
    emaLast = alpha x close + (1 - alpha) x nz(ema[0]) with ema[0] = 0 -> alpha x close;  previousState = emaLast2 > emaLast1 ? 0 : 1 (alpha2 < alpha1: always 1)
    currentState = ema2 > ema1 ? 0 : 1;  lineCheck = convergence ? checkLines(current, previous) : na;  lineCheck == 1 -> entry Long, else entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * emaLastLen1 / 2 read ema[0], the fresh 0.0 of the same bar, so they are alpha x close and the
      previous state is 1 on every bar (2 / 61 < 2 / 31). lineCheck is then 0 (current 0 against previous 1)
      or na, never 1, so the else branch sends a Short entry on every bar: one short is held from the
      first bar, as written (owed: the intended crossing logic). Short only: Opposite entries cannot
      occur. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA state comparison (degenerate as written).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only: Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438507_parker_ma_state_short_held"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [30, 10],
    "len2": [60, 120],
}
DEFAULT_PARAMS = {"len1": 30, "len2": 60}


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


def _zero_seed_ema(x, n):
    a = 2.0 / (n + 1)
    v = x.to_numpy(dtype=float)
    out = np.zeros(len(v))
    prev = 0.0
    for i in range(len(v)):
        out[i] = a * v[i] + (1 - a) * prev
        prev = 0.0 if np.isnan(out[i]) else out[i]
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n1, n2 = int(p["len1"]), int(p["len2"])
    e1, e2 = _zero_seed_ema(c, n1), _zero_seed_ema(c, n2)
    cv = c.to_numpy(dtype=float)
    last1, last2 = 2.0 / (n1 + 1) * cv, 2.0 / (n2 + 1) * cv    # ema[0] is the fresh 0.0
    prev_state = np.where(last2 > last1, 0, 1)
    cur_state = np.where(e2 > e1, 0, 1)
    conv = cur_state != prev_state
    line = np.where(conv, (cur_state > prev_state).astype(float), np.nan)
    le = line == 1
    se = ~le
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
