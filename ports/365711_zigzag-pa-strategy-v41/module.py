"""ZigZag PA Strategy (RicardoSantos): a candle-colour zigzag gives the last five swing points;
a bullish harmonic pattern (Bat, Gartley, Crab, ABCD, ...) with the close at or below the 0.236
retracement of the last leg goes long; it closes at the 0.618 target or the -0.236 stop level
(bar high / low checked at the close). Shorts mirror.
Port of FMZ strategy #365711 "[STRATEGY][RS]ZigZag PA Strategy V4.1".

Source
    https://www.fmz.com/strategy/365711 (PineScript v2/v3 syntax with some v5 calls, FMZ last
    modified 2022-05-25 18:08:49). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 73-305), alt timeframe 60 (= the 1 h chart), target 1
(entry window 0.236, TP 0.618, SL -0.236); target 2 inactive
    zigzag: on a colour change (up -> down) highest(2), (down -> up) lowest(2), unless repeating
    x, a, b, c, d = the last five zigzag points; xab, xad, abc, bcd ratios; 17 pattern tests
    fib(r) = d > c ? d - |d - c| r : d + |d - c| r
    buy  = any bullish pattern (d < c) and close <= fib(0.236)
    close_buy = high >= fib(0.618) or low <= fib(-0.236)      (sells mirror, d > c)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The alternate timeframe "60" equals the 1-hour chart, so request.security returns the chart
      series (no higher-timeframe read).
    * strategy.close runs at the bar close (it checks that bar's high / low) and fills at the next
      open: an exit signal, not a stop. A close on the bar its own entry is placed does not apply;
      an entry while already on that side is ignored (pyramiding 0); entries reverse.
    * Trade size 10000 and the inactive target 2 -> original_sizing.txt / not ported.
    * REVERSAL INTENDED (portfolio_kwargs {}). FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365711_zigzag_harmonic_patterns"
FAMILY = "pivot_reversal"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ew_rate": [0.236, 0.382],
    "tp_rate": [0.618, 1.0],
    "sl_rate": [-0.236, -0.382],
}
DEFAULT_PARAMS = {"ew_rate": 0.236, "tp_rate": 0.618, "sl_rate": -0.236}

# (xab, abc, bcd, xad) ranges per pattern; None = not tested (source lines 99-214)
PATTERNS = {
    "bat": ((0.382, 0.5), (0.382, 0.886), (1.618, 2.618), (None, 0.618)),
    "anti_bat": ((0.5, 0.886), (1.0, 2.618), (1.618, 2.618), (0.886, 1.0)),
    "alt_bat": ((None, 0.382), (0.382, 0.886), (2.0, 3.618), (None, 1.13)),
    "butterfly": ((None, 0.786), (0.382, 0.886), (1.618, 2.618), (1.27, 1.618)),
    "anti_butterfly": ((0.236, 0.886), (1.13, 2.618), (1.0, 1.382), (0.5, 0.886)),
    "abcd": (None, (0.382, 0.886), (1.13, 2.618), None),
    "gartley": ((0.5, 0.618), (0.382, 0.886), (1.13, 2.618), (0.75, 0.875)),
    "anti_gartley": ((0.5, 0.886), (1.0, 2.618), (1.5, 5.0), (1.0, 5.0)),
    "crab": ((0.5, 0.875), (0.382, 0.886), (2.0, 5.0), (1.382, 5.0)),
    "anti_crab": ((0.25, 0.5), (1.13, 2.618), (1.618, 2.618), (0.5, 0.75)),
    "shark": ((0.5, 0.875), (1.13, 1.618), (1.27, 2.24), (0.886, 1.13)),
    "anti_shark": ((0.382, 0.875), (0.5, 1.0), (1.25, 2.618), (0.5, 1.25)),
    "5o": ((1.13, 1.618), (1.618, 2.24), (0.5, 0.625), (0.0, 0.236)),
    "wolf": ((1.27, 1.618), (0.0, 5.0), (1.27, 1.618), (0.0, 5.0)),
    "hns": ((2.0, 10.0), (0.9, 1.1), (0.236, 0.88), (0.9, 1.1)),
    "con_tria": ((0.382, 0.618), (0.382, 0.618), (0.382, 0.618), (0.236, 0.764)),
    "exp_tria": ((1.236, 1.618), (1.0, 1.618), (1.236, 2.0), (2.0, 2.236)),
}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _zigzag(bars):
    o, c = bars["open"].to_numpy(dtype=float), bars["close"].to_numpy(dtype=float)
    h, l = bars["high"].to_numpy(dtype=float), bars["low"].to_numpy(dtype=float)
    up, dn = c >= o, c <= o
    m = len(c)
    zz = np.full(m, np.nan)
    d = 0
    for i in range(1, m):
        d_prev = d
        if up[i - 1] and dn[i]:
            d = -1
        elif dn[i - 1] and up[i]:
            d = 1
        if up[i - 1] and dn[i] and d_prev != -1:
            zz[i] = max(h[i], h[i - 1])
        elif dn[i - 1] and up[i] and d_prev != 1:
            zz[i] = min(l[i], l[i - 1])
    return zz


def _in(v, rng):
    if rng is None:
        return True
    lo, hi = rng
    return (lo is None or v >= lo) and v <= hi


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    zz = _zigzag(bars_df)
    h, l, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pts = []
    pos = 0
    for i in range(m):
        if not np.isnan(zz[i]) and zz[i] != 0:
            pts.append(zz[i])
            del pts[:-5]
        if len(pts) < 2:
            continue
        cc, dd = pts[-2], pts[-1]
        rng = abs(dd - cc)
        fib = lambda r: dd - rng * r if dd > cc else dd + rng * r
        bull = bear = False
        if len(pts) == 5:
            x, a, b = pts[0], pts[1], pts[2]
            with np.errstate(all="ignore"):
                r = (np.float64(abs(b - a)) / abs(x - a), np.float64(abs(b - cc)) / abs(a - b),
                     np.float64(abs(cc - dd)) / abs(b - cc), np.float64(abs(a - dd)) / abs(x - a))
            hit = any(all(_in(v, rg) for v, rg in zip(r, spec)) for spec in PATTERNS.values())
            bull, bear = hit and dd < cc, hit and dd > cc
        buy = bull and c[i] <= fib(p["ew_rate"])
        sell = bear and c[i] >= fib(p["ew_rate"])
        buy_close = h[i] >= fib(p["tp_rate"]) or l[i] <= fib(p["sl_rate"])
        sell_close = l[i] <= fib(p["tp_rate"]) or h[i] >= fib(p["sl_rate"])
        before = pos
        if buy and before != 1:
            le[i], pos = True, 1
        elif sell and before != -1:
            se[i], pos = True, -1
        if not le[i] and not se[i]:
            if buy_close and before == 1:
                lx[i], pos = True, 0
            elif sell_close and before == -1:
                sx[i], pos = True, 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
