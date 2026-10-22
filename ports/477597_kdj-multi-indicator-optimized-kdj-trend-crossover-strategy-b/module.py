"""KDJ (90-bar RSV, K smoothing 3, D smoothing 30) J / D crossings, 4-hour bars, long only: J crossing over D buys, D crossing over J closes; a 5 % stop from the entry price.
Port of FMZ strategy #477597 "多指标优化型KDJ趋势交叉策略基于动态随机形态的交易系统-Multi-Indicator-Optimized-KDJ-Trend-Crossover-Strategy-Based-on-Dynamic-Stochastic-Pattern-Trading-System" (My KDJ Strategy).

FMZ source id: 477597

Source
    https://www.fmz.com/strategy/477597 (PineScript v6, FMZ last modified 2025-01-06 16:23:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-222), period 90; K signal 3, D signal 30 (weighted recursive smoothing, weight 1); stop 5 % of strategy.position_avg_price; qty 1; trailing inputs unused
    rsv = 100 (close - lowest(low, 90)) / (highest(high, 90) - lowest(low, 90));  k = bcwsma(rsv, 3, 1);  d = bcwsma(k, 30, 1);  j = 3k - 2d
    crossover(j, d) -> entry golden (qty 1);  crossover(d, j) -> close golden;  every bar: exit(golden, stop = avg x 0.95)

Interpretation choices (Pine rules in SURVEY_README.md)
    * bcwsma keeps its own value: it starts at the source on the first bar the value is na and then
      moves by (source + (length - 1) x previous) / length (a loop, as written; an na source makes it na
      and it restarts on the next bar). The condition counters, the consecutive-day count and the
      trailing inputs do not trade. The stop is sent from the position's average price: a scalar fraction
      of the entry fill, active from the fill (as #440797). Long only. Stop module: portfolio_kwargs {}
      (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. The fixed qty 1 is sizing. FREQ
      = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; avg-price stop as a fraction of the fill.
    2 generic: PASS, KDJ J / D crossings with a percent stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 stored, not ported; the stop percentage stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_477597_kdj90_3_30_jd_cross_pct_stop_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "period": [90, 30],
    "d_signal": [30, 10],
}
DEFAULT_PARAMS = {"period": 90, "d_signal": 30, "k_signal": 3, "sl_pct": 0.05}


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


def _bcwsma(v, length, weight=1.0):
    """The script's bcwsma: var prev, set to the source while na, then (w src + (L - w) prev) / L."""
    out = np.full(len(v), np.nan)
    prev = np.nan
    for i in range(len(v)):
        if np.isnan(prev):
            prev = v[i]
        prev = (weight * v[i] + (length - weight) * prev) / length
        out[i] = prev
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["period"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    rsv = (100 * (c - ll) / (hh - ll).where(hh != ll)).to_numpy(dtype=float)
    k = _bcwsma(rsv, int(p["k_signal"]))
    d = _bcwsma(k, int(p["d_signal"]))
    j = pd.Series(3 * k - 2 * d, index=c.index)
    ds = pd.Series(d, index=c.index)
    le = (j > ds) & (j.shift(1) <= ds.shift(1))
    lx = (ds > j) & (ds.shift(1) <= j.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
