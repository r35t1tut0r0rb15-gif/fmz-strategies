"""A vote of 17 averages and oscillators against the close, 1-hour bars: with (votes below the close) - (votes above) over 12 it goes long, under -12 it goes short; the count falling under -9 closes a long, rising over 9 closes a short; reversing.
Port of FMZ strategy #455353 "EMA-SMA多指标综合趋势跟踪策略-EMA-SMA-Multi-Indicator-Comprehensive-Trend-Following-Strategy" (EMA/SMA Above-Below Close with Multiple Indicators).

FMZ source id: 455353

Source
    https://www.fmz.com/strategy/455353 (PineScript v5, FMZ last modified 2024-06-28 15:00:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 195-287), EMA / SMA 10 / 20 / 30 / 50 / 100 / 200; RSI 14 vs 50; stochastic 14 (80 / 20); CCI 20 (+- 100); momentum 10; MACD 12 / 26 / 9 histogram; entry 12 / -12, close -9 / 9
    diff = below_count - above_count;  diff > 9 -> close Sell;  diff < -9 -> close Buy;  diff > 12 -> entry Buy;  diff < -12 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each count adds one per average above (below) the close and per oscillator reading on its side,
      as written ('below' means the average is under the close). The closes run before the entries: a
      close and an opposite entry on one bar are one reversal. Both entries are states (repeats
      ignored). REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, multi-indicator vote thresholds.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_455353_seventeen_indicator_vote_threshold_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "entry_lvl": [12, 10, 14],
    "close_lvl": [9, 5],
}
DEFAULT_PARAMS = {"entry_lvl": 12, "close_lvl": 9}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    mas = []
    for n in (10, 20, 30, 50, 100, 200):
        mas.append(c.ewm(span=n, adjust=False).mean())
        mas.append(c.rolling(n).mean())
    r = _rsi(c, 14)
    hh, ll = h.rolling(14).max(), lo.rolling(14).min()
    rng = hh - ll
    st = 100 * (c - ll) / rng.where(rng > 0)
    sma20 = c.rolling(20).mean()
    mad = c.rolling(20).apply(lambda v: np.abs(v - v.mean()).mean(), raw=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        cci = (c - sma20) / (0.015 * mad)
    mom = c - c.shift(10)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    above = sum((ma > c).astype(int) for ma in mas)
    above = above + (r > 50).astype(int) + (st > 80).astype(int) + (cci > 100).astype(int) \
        + (mom > 0).astype(int) + (hist > 0).astype(int)
    below = sum((ma < c).astype(int) for ma in mas)
    below = below + (r < 50).astype(int) + (st < 20).astype(int) + (cci < -100).astype(int) \
        + (mom < 0).astype(int) + (hist < 0).astype(int)
    d = (below - above).to_numpy()
    el, cl = float(p["entry_lvl"]), float(p["close_lvl"])
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if d[i] > cl and pos == -1:
            cur = 0
        if d[i] < -cl and pos == 1:
            cur = 0
        if d[i] > el and cur != 1:
            cur = 1
        if d[i] < -el and cur != -1:
            cur = -1
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
