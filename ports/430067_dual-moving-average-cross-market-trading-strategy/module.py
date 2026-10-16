"""Swing HULL + T3, 1-hour bars: the average of an HMA 50 and a T3 50 (factor 0.7) rising holds a long, falling holds a
short; longs take profit 8 % away, shorts take profit 3 % and stop 6 % away (fixed at the fill; the source re-sizes
them from each bar's close).
Port of FMZ strategy #430067 "Dual Moving Average Cross Market Trading Strategy" (Swing HULL + T3 avg).

FMZ source id: 430067

Source
    https://www.fmz.com/strategy/430067 (PineScript v4, FMZ last modified 2023-10-24 16:55:38).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 118-197), HMA 50, T3 50 / 0.7, TP long 8 %, SL long 100 %, TP short 3 %, SL short 6 %
    avg = (hma(close, 50) + t3(close, 50, 0.7)) / 2
    avg > avg[1] -> entry long; exit(profit = close x 0.08 / mintick, loss = close x 1.0 / mintick)
    avg < avg[1] -> entry short; exit(profit = close x 0.03 / mintick, loss = close x 0.06 / mintick)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-issued every bar with distances in ticks of the CURRENT close, so the levels
      move after entry: rule 2, mark trailing_stop_pending. The port fixes them at the same fractions
      of the fill price (long tp_stop 0.08; short tp_stop 0.03, sl_stop 0.06), side taken from the
      signal bar (the fractions are shifted one bar to the fill).
    * The long stop at 100 % of the close sits at a price of about zero: unreachable, not emitted.
    * The 2000-2021 date inputs are unused (time_cond = true).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving exit levels fixed at the fill (rule 2).
    2 generic: PASS, moving-average slopes and percentage exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the exit distances quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_430067_hull_t3_swing"
FAMILY = "hull_ma"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [50, 30],
    "tp_long": [0.08, 0.04],
}
DEFAULT_PARAMS = {"length": 50, "v_factor": 0.7, "tp_long": 0.08, "tp_short": 0.03, "sl_short": 0.06}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(x, n):
    return _wma(2 * _wma(x, int(n / 2)) - _wma(x, n), int(round(np.sqrt(n))))


def _t3(x, n, v):
    e = [x]
    for _ in range(6):
        e.append(e[-1].ewm(span=n, adjust=False).mean())
    c1 = -v ** 3
    c2 = 3 * v ** 2 + 3 * v ** 3
    c3 = -6 * v ** 2 - 3 * v - 3 * v ** 3
    c4 = 1 + 3 * v + v ** 3 + 3 * v ** 2
    return c1 * e[6] + c2 * e[5] + c3 * e[4] + c4 * e[3]


def _sides(bars_df, p):
    c = bars_df["close"]
    n = int(p["length"])
    avg = (_hma(c, n) + _t3(c, n, float(p["v_factor"]))) / 2
    return (avg > avg.shift(1)).astype(bool), (avg < avg.shift(1)).astype(bool)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _sides(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _sides(bars_df, p)
    idx = bars_df.index
    tp = pd.Series(np.where(long_e, p["tp_long"], np.where(short_e, p["tp_short"], np.nan)), index=idx)
    sl = pd.Series(np.where(short_e, p["sl_short"], np.nan), index=idx)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
