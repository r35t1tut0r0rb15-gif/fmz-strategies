"""MACD histogram zero crossings with an RSI side filter, or RSI level crossings with the histogram's sign, 1-hour bars: the histogram crossing over zero with the RSI 14 above 40, or the RSI crossing over 40
with the histogram positive, goes long; the mirror (RSI under 60 / crossing under 60) goes short; reversing.
Port of FMZ strategy #444963 "基于RSI和MACD交叉策略The-RSI-and-MACD-Crossover-Strategy" (RSIand macd bull and bear).

FMZ source id: 444963

Source
    https://www.fmz.com/strategy/444963 (PineScript v5, FMZ last modified 2024-03-15 15:08:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 175-242), RSI 14, levels 60 / 40; MACD 12 / 26 / 9; EMA 10 / 20 (plot only)
    (rsi > 40 and crossover(hist, 0)) or (crossover(rsi, 40) and hist > 0) -> entry Buy;  (rsi < 60 and crossunder(hist, 0)) or (crossunder(rsi, 60) and hist < 0) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * "and" binds before "or" in Pine, so each condition is two alternatives, as ported. The exit
      blocks are commented out: positions end at the opposite entry. The EMAs only colour the chart.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram and RSI crossings.
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

NAME = "fmz_444963_macd_hist_zero_rsi_side_cross_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "oversold": [40, 30],
}
DEFAULT_PARAMS = {"length": 14, "oversold": 40.0, "overbought": 60.0}


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
    r = _rsi(c, int(p["length"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    h1, r1 = hist.shift(1), r.shift(1)
    os_, ob = float(p["oversold"]), float(p["overbought"])
    buy = ((r > os_) & (hist > 0) & (h1 <= 0)) | ((r > os_) & (r1 <= os_) & (hist > 0))
    sell = ((r < ob) & (hist < 0) & (h1 >= 0)) | ((r < ob) & (r1 >= ob) & (hist < 0))
    false = pd.Series(False, index=bars_df.index)
    return buy & ~sell, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
