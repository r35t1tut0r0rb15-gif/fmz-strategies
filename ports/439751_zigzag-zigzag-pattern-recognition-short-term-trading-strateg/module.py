"""Harmonic patterns on a 1-hour candle-colour ZigZag, 2-hour bars: when the last five ZigZag points (X A B C D) fit any of the script's 17 pattern ratio boxes with D under C, a close at or under the 0.382
retracement of C-D goes long; the mirror goes short; the 0.618 target or the -0.618 stop level touched closes; reversing.
Port of FMZ strategy #439751 "基于ZigZag的多种形态识别短线交易策略ZigZag-Pattern-Recognition-Short-term-Trading-Strategy" ([STRATEGY][RS]ZigZag PA Strategy V4).

FMZ source id: 439751

Source
    https://www.fmz.com/strategy/439751 (PineScript v4, FMZ last modified 2024-01-23 15:09:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 124-352), Heikin-Ashi off; alt timeframe on, "60"; entry window 0.382, target 0.618, stop -0.618; trade size 1
    zigzag (on "60"): a colour change from up to down marks highest(2), from down to up lowest(2), each only once per direction;  sz = the zigzag of the 1-hour series
    x, a, b, c, d = the last five zigzag values;  xab, xad, abc, bcd ratios;  17 pattern boxes (Bat ... Expanding Triangle), mode 1 needs d < c, mode -1 d > c
    buy_entry = any pattern(1) and close <= fib(0.382);  buy_close = high >= fib(0.618) or low <= fib(-0.618);  sell mirror;  entry buy, close buy, entry sell, close sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * A lower time frame requested from a 2-hour chart returns its last bar inside the chart bar (as
      #436765): the zigzag runs on 1-hour bars built from the module's minutes and each 2-hour bar takes
      the value of its last 1-hour bar (a point on the first hour is not seen, as written). time("60")
      changes on every chart bar, so the alternate series is always used. fib(r) is d -/+ r |d - c|
      toward C. The closes are bar-close tests of the bar's high / low against the levels. They act on
      the position held at the bar close: a close of the side just reversed out of meets no position
      and the reversal stands (as #438020). strategy.entry reverses: REVERSAL INTENDED. The trade size
      is sizing. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; lower-time-frame zigzag from its last bar.
    2 generic: PASS, zigzag ratios and Fibonacci levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the trade size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND365711 (2 members, best partner #365711, Jaccard 0.688); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439751_zigzag_harmonic_patterns_fib_window"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ew_rate": [0.382, 0.5],
    "tp_rate": [0.618, 1.0],
}
DEFAULT_PARAMS = {"ew_rate": 0.382, "tp_rate": 0.618, "sl_rate": -0.618}

INF = float("inf")
# (xab lo, xab hi, abc lo, abc hi, bcd lo, bcd hi, xad lo, xad hi); None = not tested
PATTERNS = (
    (0.382, 0.5, 0.382, 0.886, 1.618, 2.618, -INF, 0.618),        # Bat
    (0.5, 0.886, 1.0, 2.618, 1.618, 2.618, 0.886, 1.0),           # Anti Bat
    (-INF, 0.382, 0.382, 0.886, 2.0, 3.618, -INF, 1.13),          # Alt Bat
    (-INF, 0.786, 0.382, 0.886, 1.618, 2.618, 1.27, 1.618),       # Butterfly
    (0.236, 0.886, 1.13, 2.618, 1.0, 1.382, 0.5, 0.886),          # Anti Butterfly
    (None, None, 0.382, 0.886, 1.13, 2.618, None, None),          # AB=CD
    (0.5, 0.618, 0.382, 0.886, 1.13, 2.618, 0.75, 0.875),         # Gartley
    (0.5, 0.886, 1.0, 2.618, 1.5, 5.0, 1.0, 5.0),                 # Anti Gartley
    (0.5, 0.875, 0.382, 0.886, 2.0, 5.0, 1.382, 5.0),             # Crab
    (0.25, 0.5, 1.13, 2.618, 1.618, 2.618, 0.5, 0.75),            # Anti Crab
    (0.5, 0.875, 1.13, 1.618, 1.27, 2.24, 0.886, 1.13),           # Shark
    (0.382, 0.875, 0.5, 1.0, 1.25, 2.618, 0.5, 1.25),             # Anti Shark
    (1.13, 1.618, 1.618, 2.24, 0.5, 0.625, 0.0, 0.236),           # 5-O
    (1.27, 1.618, 0.0, 5.0, 1.27, 1.618, 0.0, 5.0),               # Wolf
    (2.0, 10.0, 0.9, 1.1, 0.236, 0.88, 0.9, 1.1),                 # Head and Shoulders
    (0.382, 0.618, 0.382, 0.618, 0.382, 0.618, 0.236, 0.764),     # Contracting Triangle
    (1.236, 1.618, 1.0, 1.618, 1.236, 2.0, 2.0, 2.236),           # Expanding Triangle
)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _zigzag(b):
    o, h, lo, c = (b[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    up, dn = c >= o, c <= o
    m = len(c)
    d = np.zeros(m)
    zz = np.full(m, np.nan)
    for i in range(1, m):
        if up[i - 1] and dn[i]:
            d[i] = -1
        elif dn[i - 1] and up[i]:
            d[i] = 1
        else:
            d[i] = d[i - 1]
        if up[i - 1] and dn[i] and d[i - 1] != -1:
            zz[i] = max(h[i], h[i - 1])
        elif dn[i - 1] and up[i] and d[i - 1] != 1:
            zz[i] = min(lo[i], lo[i - 1])
    return zz


def precompute(raw_1m_df, symbol_key, **params):
    bars = _resample(raw_1m_df, FREQ)
    b60 = _resample(raw_1m_df, "60min")
    zz = _zigzag(b60)
    lab = b60.index.floor(FREQ)
    last = ~lab.duplicated(keep="last")                      # the last 1-hour bar inside each 2-hour bar
    sz = pd.Series(zz[last], index=lab[last])
    bars["sz"] = sz.reindex(bars.index).to_numpy()
    return bars


def _box(v, lo, hi):
    if lo is None:
        return np.ones(len(v), dtype=bool)
    with np.errstate(invalid="ignore"):
        return (v >= lo) & (v <= hi)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sz = bars_df["sz"].to_numpy(dtype=float)
    m = len(sz)
    pts = np.full((m, 5), np.nan)                            # x, a, b, c, d
    hist = []
    for i in range(m):
        v = sz[i]
        if not np.isnan(v) and v != 0:
            hist.append(v)
            hist = hist[-5:]
        if hist:
            row = [np.nan] * (5 - len(hist)) + hist
            pts[i] = row
    x, a, b, c, d = (pts[:, k] for k in range(5))
    with np.errstate(divide="ignore", invalid="ignore"):
        xab = np.abs(b - a) / np.abs(x - a)
        xad = np.abs(a - d) / np.abs(x - a)
        abc = np.abs(b - c) / np.abs(a - b)
        bcd = np.abs(c - d) / np.abs(b - c)
    match = np.zeros(m, dtype=bool)
    for q in PATTERNS:
        match |= _box(xab, q[0], q[1]) & _box(abc, q[2], q[3]) & _box(bcd, q[4], q[5]) & _box(xad, q[6], q[7])
    rng = np.abs(d - c)

    def fib(r):
        return np.where(d > c, d - rng * r, d + rng * r)

    cv = bars_df["close"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    ew, tp, sl = fib(float(p["ew_rate"])), fib(float(p["tp_rate"])), fib(float(p["sl_rate"]))
    with np.errstate(invalid="ignore"):
        be = match & (d < c) & (cv <= ew)
        bc = (hv >= tp) | (lv <= sl)
        se = match & (d > c) & (cv >= ew)
        sc = (lv <= tp) | (hv >= sl)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if be[i] and pos != 1:
            new = 1
        if pos == 1 and bc[i] and new == 1:
            new = 0
        if se[i] and new != -1:
            new = -1
        if pos == -1 and sc[i] and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
