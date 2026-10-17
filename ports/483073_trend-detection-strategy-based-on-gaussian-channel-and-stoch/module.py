"""Gaussian-filter channel re-entries with stochastic extremes, 1-hour bars: the close crossing above the lower
channel (filter - 2 %) while %K and %D are below 20 goes long; crossing below the upper channel (filter + 2 %) while
both are above 80 goes short; a long closes on a cross below the filter or %K and %D above 80 (a short mirrored).
Port of FMZ strategy #483073 "基于高斯通道与随机相对强弱指数过滤的趋势判断策略-Trend-Detection-Strategy-Based-on-Gaussian-Channel-and-Stochastic-RSI-Filter" (Gaussian Channel + Stochastic RSI Filter).

FMZ source id: 483073

Source
    https://www.fmz.com/strategy/483073 (PineScript v6, FMZ last modified 2025-02-21 11:42:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 123-190), length 100, multiplier 2 %, stochastic 14 / 3 / 3 (80 / 20)
    mid = f, f = a0 x close + b x f[1] (b = exp(-1.414 x 3.14159 / 100), a0 = 1 - b; f = close on the first bar)
    long = crossover(close, mid x 0.98) and k < 20 and d < 20; short = crossunder(close, mid x 1.02) and k > 80, d > 80
    long_exit = crossunder(close, mid) or (k > 80 and d > 80); short_exit = crossover(close, mid) or (k < 20, d < 20)
    order: entry long, entry short, close long, close short; close_all before 2023-01-01

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "Stochastic RSI" is ta.stoch of price (close, high, low), as written.
    * The closes come after the entries: they act on the position held at the bar's start and never undo an entry on
      that bar (as #430850); a long and a short entry on one bar: the later short wins. Target-position state machine,
      exits only on going flat. Entries reverse (REVERSAL INTENDED). No stops.
    * Clock rule (C6): before timestamp(2023, 1, 1) in the chart's zone (UTC on Binance) every bar runs close_all: the
      port holds no position before 2023-01-01 00:00 UTC (Pine would open and close one-bar trades there). The 2069 end
      is beyond the data.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a recursive filter channel in percent and a stochastic.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (a start date 2023-01-01 00:00 UTC, declared above).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483073_gaussian_channel_stoch_reentry"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50],
    "mult": [2.0, 1.0],
}
DEFAULT_PARAMS = {"length": 100, "mult": 2.0, "k_len": 14, "k_smooth": 3, "d_smooth": 3, "ob": 80.0, "os": 20.0,
                  "start_date": "2023-01-01"}


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


def _gauss(v, n):
    b = np.exp(-1.414 * 3.14159 / n)
    a0 = 1 - b
    out = np.full(len(v), np.nan)
    prev = np.nan
    for i, x in enumerate(v):
        f = x if np.isnan(prev) else a0 * x + b * prev
        out[i] = f
        prev = f
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    mid = pd.Series(_gauss(c.to_numpy(dtype=float), int(p["length"])), index=c.index)
    hi_b, lo_b = mid * (1 + p["mult"] / 100), mid * (1 - p["mult"] / 100)
    n = int(p["k_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["k_smooth"])).mean()
    d = k.rolling(int(p["d_smooth"])).mean()
    os_ = ((k < p["os"]) & (d < p["os"])).to_numpy()
    ob = ((k > p["ob"]) & (d > p["ob"])).to_numpy()
    c1 = c.shift(1)
    long_c = ((c > lo_b) & (c1 <= lo_b.shift(1))).to_numpy() & os_
    short_c = ((c < hi_b) & (c1 >= hi_b.shift(1))).to_numpy() & ob
    x_long = ((c < mid) & (c1 >= mid.shift(1))).to_numpy() | ob
    x_short = ((c > mid) & (c1 <= mid.shift(1))).to_numpy() | os_
    live = np.asarray(bars_df.index >= pd.Timestamp(p["start_date"], tz="UTC"))
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if not live[i]:
            pos = 0
            continue
        start = pos
        if long_c[i]:
            pos = 1
        if short_c[i]:
            pos = -1
        if x_long[i] and start == 1 and pos == 1:
            pos = 0
        if x_short[i] and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
