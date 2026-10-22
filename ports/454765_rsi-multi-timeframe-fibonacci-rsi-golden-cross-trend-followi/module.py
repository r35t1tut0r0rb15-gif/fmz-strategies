"""SMA 50 / 200 golden and death crosses on the side of the 50-close range midpoint, 1-hour bars: the golden cross with the close over the midpoint and the RSI under 70 goes long, the death cross under it with the RSI over 30 goes short; an RSI over 70 closes the long, under 30 the short; reversing.
Port of FMZ strategy #454765 "多周期斐波那契RSI黄金交叉趋势跟踪量化交易策略-Multi-Timeframe-Fibonacci-RSI-Golden-Cross-Trend-Following-Quantitative-Trading-Strategy" (15min Fibonacci RSI Golden Cross Scalping Strategy).

FMZ source id: 454765

Source
    https://www.fmz.com/strategy/454765 (PineScript v5, FMZ last modified 2024-06-21 18:07:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 136-208), SMA 50 / 200; RSI 14; fib 50 % of the highest / lowest close of 50 bars (set when they change)
    golden cross and close > fib50 and rsi < 70 -> entry Buy;  death cross and close < fib50 and rsi > 30 -> entry Sell
    long and rsi > 70 -> close Buy;  short and rsi < 30 -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The var high / low take the 50-bar highest / lowest close whenever it changes, so after both
      have changed once they equal it; the 50 % level is their midpoint. The entries are called before
      the closes; an opposite entry reverses and the close then finds the trade reversed. REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, golden / death crosses with a range-midpoint side and RSI exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454765_golden_cross_range_mid_rsi_exit_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [50, 20],
    "long_len": [200, 100],
    "fib_len": [50, 100],
}
DEFAULT_PARAMS = {"short_len": 50, "long_len": 200, "fib_len": 50, "rsi_len": 14}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["fib_len"])
    hh, ll = c.rolling(n).max().to_numpy(), c.rolling(n).min().to_numpy()
    m = len(c)
    fh = fl = np.nan
    mid = np.full(m, np.nan)
    for i in range(1, m):
        if not np.isnan(hh[i]) and not np.isnan(hh[i - 1]) and hh[i] != hh[i - 1]:
            fh = hh[i]
        if not np.isnan(ll[i]) and not np.isnan(ll[i - 1]) and ll[i] != ll[i - 1]:
            fl = ll[i]
        if not np.isnan(fh) and not np.isnan(fl):
            mid[i] = fh - (fh - fl) * 0.5
    cv = c.to_numpy(dtype=float)
    a = c.rolling(int(p["short_len"])).mean()
    b = c.rolling(int(p["long_len"])).mean()
    gold = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    death = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    r = _rsi(c, int(p["rsi_len"])).to_numpy()
    with np.errstate(invalid="ignore"):
        el = gold & (cv > mid) & (r < 70)
        es = death & (cv < mid) & (r > 30)
        xl, xs = r > 70, r < 30
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if el[i] and cur != 1:
            cur = 1
        if es[i] and cur != -1:
            cur = -1
        if xl[i] and pos == 1 and cur == 1:
            cur = 0
        if xs[i] and pos == -1 and cur == -1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
