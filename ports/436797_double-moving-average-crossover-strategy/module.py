"""Parabolic SAR side with an ALMA crossing, 1-hour bars: an up candle whose low is above the SAR, closing across over the ALMA 50, goes long; a down candle whose high is under the SAR, closing across under it, goes
short; reversing.
Port of FMZ strategy #436797 "Double Moving Average Crossover Strategy" (ST-PSAR+ALMA).

FMZ source id: 436797

Source
    https://www.fmz.com/strategy/436797 (PineScript v3, FMZ last modified 2023-12-27 17:45:43).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 187-204), ALMA 50 / offset 0.85 / sigma 6; SAR 0.02 / 0.02 / 0.2
    long = close > open and sar(0.02, 0.02, 0.2) < low and crossover(close, alma(close, 50, 0.85, 6)) -> entry Long
    short = close < open and sar > high and crossunder(close, alma) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * alma weights the window oldest to newest with a Gaussian centred at offset x (window - 1), sigma
      window / 6, as Pine's reference code. sar is Pine's reference implementation. Entries are signals
      only; positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SAR side and an average crossing.
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

NAME = "fmz_436797_psar_alma_cross"
FAMILY = "trend_confluence"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "window": [50, 30],
    "sigma": [6.0, 4.0],
}
DEFAULT_PARAMS = {"window": 50, "sigma": 6.0, "offset": 0.85, "psar_start": 0.02, "psar_inc": 0.02,
                  "psar_max": 0.2}


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


def _sar(h, lo, c, start, inc, mx):
    """Pine's sar(start, inc, max), as the reference implementation in the Pine manual."""
    n = len(c)
    out = np.full(n, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, n):
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
            if below:
                if h[i] > max_min:
                    max_min, acc = h[i], min(acc + inc, mx)
            else:
                if lo[i] < max_min:
                    max_min, acc = lo[i], min(acc + inc, mx)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return out


def _alma(x, n, offset, sigma):
    m = offset * (n - 1)
    s = n / sigma
    w = np.exp(-((np.arange(n) - m) ** 2) / (2 * s * s))     # oldest first, as Pine's loop
    w = w / w.sum()
    return x.rolling(n).apply(lambda v: np.dot(v, w), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         float(p["psar_start"]), float(p["psar_inc"]), float(p["psar_max"])), index=c.index)
    al = _alma(c, int(p["window"]), float(p["offset"]), float(p["sigma"]))
    up = (c > o) & (sar < lo) & (c > al) & (c.shift(1) <= al.shift(1))
    dn = (c < o) & (sar > h) & (c < al) & (c.shift(1) >= al.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
