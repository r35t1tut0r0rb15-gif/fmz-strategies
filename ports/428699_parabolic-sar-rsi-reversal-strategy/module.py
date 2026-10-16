"""Parabolic SAR flips, 2-hour bars: the SAR crossing under the close goes long, crossing over it goes
short (the RSI exits are commented out in the source).
Port of FMZ strategy #428699 "Parabolic SAR RSI Reversal Strategy" (SARSI).

FMZ source id: 428699

Source
    https://www.fmz.com/strategy/428699 (PineScript v3, FMZ last modified 2023-10-08 14:21:17).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 183-203), SAR 0.007 / 0.017 / 0.24, source close
    up = crossunder(sar, close) -> entry long; dn = crossover(sar, close) -> entry short
    (strategy.close on RSI 82 / 21 commented out)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line, with calc_on_every_tick and calc_on_order_fills, is commented out, so
      the defaults apply: bar-close evaluation, orders at the next open. The RSI is computed but its
      exits are commented out: not ported.
    * `time >= 2018-08-01` is the author's backtest window: dropped.
    * sar() as TradingView documents it (pine_sar): starts on bar 1, direction from close vs the
      previous close, capped by the previous two bars' lows (highs).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders (the intrabar settings are in a commented-out line).
    2 generic: PASS, SAR acceleration factors are dimensionless.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() line (100 % of equity, commission, capital) stored.
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

NAME = "fmz_428699_sar_close_flip"
FAMILY = "parabolic_sar"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sar_start": [0.007, 0.02],
    "sar_max": [0.24, 0.2],
}
DEFAULT_PARAMS = {"sar_start": 0.007, "sar_inc": 0.017, "sar_max": 0.24}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar): starts on bar 1, direction from close vs
    the previous close; value capped by the previous two bars' lows (highs)."""
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    out = np.full(m, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, m):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below and h[i] > max_min:
                max_min, acc = h[i], min(acc + inc, maximum)
            elif (not below) and lo[i] < max_min:
                max_min, acc = lo[i], min(acc + inc, maximum)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return pd.Series(out, index=bars.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sar = _sar_pine(bars_df, float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"]))
    long_e = ((sar < c) & (sar.shift(1) >= c.shift(1))).astype(bool)
    short_e = ((sar > c) & (sar.shift(1) <= c.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
