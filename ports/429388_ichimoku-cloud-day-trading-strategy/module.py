"""Ichimoku cloud with a parabolic SAR filter, hourly bars: above a rising (green) displaced cloud, the close
crossing over the base line with the close above the SAR goes long; the mirror goes short (the SAR trailing
stop is described, not emitted).
Port of FMZ strategy #429388 "Ichimoku Cloud Day Trading Strategy" (Ichimoku Cloud Strategy).

FMZ source id: 429388

Source
    https://www.fmz.com/strategy/429388 (PineScript v3, FMZ last modified 2023-10-16 16:10:55).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 221-271), Ichimoku 9 / 26 / 52 / 26, SAR 0.02 / 0.02 / 0.2, SAR trailing stop on
    buy = close > lead2[26] and lead1[26] > lead2[26] and crossover(close, base) and close > sar -> entry long
    sell = close < lead1[26] and lead1[26] < lead2[26] and crossunder(close, base) and close < sar -> entry short
    while in a position: exit(stop = sar) every bar (the SAR as a trailing stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lead lines read 26 bars back are the cloud drawn at the current bar (no look-ahead).
      sar() as TradingView documents it (pine_sar).
    * The SAR trailing stop moves every bar by the SAR's own rule, which stops() cannot express (not a
      percent, volatility or lock-in trail): rule 2, not emitted; mark trailing_stop_pending, described
      in PORT_NOTES. pyramiding 3 adds are sizing (stored).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the SAR trailing stop is not emitted (rule 2).
    2 generic: PASS, price vs lines from the bars only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 3 stored; the SAR stop quoted in original_sizing.txt.
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

NAME = "fmz_429388_ichimoku_sar_filter"
FAMILY = "ichimoku"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "base": [26, 52],
    "sar_max": [0.2, 0.1],
}
DEFAULT_PARAMS = {"conv": 9, "base": 26, "span2": 52, "disp": 26, "sar_start": 0.02, "sar_inc": 0.02,
                  "sar_max": 0.2}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    don = lambda n: (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2  # noqa: E731
    base = don(p["base"])
    k = int(p["disp"])
    l1 = ((don(p["conv"]) + base) / 2).shift(k)
    l2 = don(p["span2"]).shift(k)
    sar = _sar_pine(bars_df, float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"]))
    long_e = ((c > l2) & (l1 > l2) & (c > base) & (c.shift(1) <= base.shift(1)) & (c > sar)).astype(bool)
    short_e = ((c < l1) & (l1 < l2) & (c < base) & (c.shift(1) >= base.shift(1)) & (c < sar)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
