"""Close / SMA 9 cross with an RSI(9) / WMA-of-RSI cross, long only, 2-hour bars: both crossing up on one bar
goes long; both crossing down closes it; each long has a 3 % stop and a 15 % target.
Port of FMZ strategy #429393 "基于RSI和移动平均线的多时间框架交易策略RSI-and-Moving-Average-Crossover-Multi-Timeframe-Trading-Strategy" (H-M By HamidBox-YT).

FMZ source id: 429393

Source
    https://www.fmz.com/strategy/429393 (PineScript v4, FMZ last modified 2023-10-16 16:31:28).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 162-387), RSI 9, WMA 21 of RSI, SMA 9 of close, stop 3 %, target 15 %; signal type "MA + RSI x Trending-MA"
    buy = crossover(close, sma(close,9)) and crossover(rsi9, wma(rsi9,21)) -> entry long
    sell = crossunder(close, sma(close,9)) and crossunder(rsi9, wma(rsi9,21)) -> close long
    while long: exit(stop = avg x 0.97, limit = avg x 1.15)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Of the eight signal types only "MA + RSI x Trending-MA" is on by default; the others are input
      options (off). The date range is dropped (inDateRange is true).
    * The bracket is 3 % / 15 % of the average entry price (the fill): sl_stop 0.03, tp_stop 0.15.
    * The strategy() line is commented out. Long only; Opposite entries cannot occur. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark coarse_bar_stop. FREQ = "2h".

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, moving-average and RSI crosses, percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_429393_sma9_rsi_wma_cross_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [3.0, 1.5],
    "tp_pct": [15.0, 5.0],
}
DEFAULT_PARAMS = {"rsi_length": 9, "wma_length": 21, "with_ma": 9, "sl_pct": 3.0, "tp_pct": 15.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    w = _wma(r, int(p["wma_length"]))
    ma = c.rolling(int(p["with_ma"])).mean()
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))  # noqa: E731
    xu = lambda a, b: (a < b) & (a.shift(1) >= b.shift(1))  # noqa: E731
    long_e = (xo(c, ma) & xo(r, w)).astype(bool)
    long_x = (xu(c, ma) & xu(r, w)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100, "tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
