"""UT Bot ATR trailing line, 1-hour bars: the close crossing over the 10 x ATR(10) trailing line goes long, crossing under goes short; reversing.
Port of FMZ strategy #439710 "基于ATR和RSI的自适应移动止损趋势跟踪策略Adaptive-ATR-and-RSI-Trend-Following-Strategy-with-Trailing-Stop-Loss" (UTBot Strategy).

FMZ source id: 439710

Source
    https://www.fmz.com/strategy/439710 (PineScript v2, FMZ last modified 2024-01-23 11:31:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 139-198), key value 10; ATR 10; the RSI, MACD and stochastic inputs unused; test period true
    xATRTrailingStop = close > prev and close[1] > prev ? max(prev, close - 10 atr) : close < prev and close[1] < prev ? min(prev, close + 10 atr) : close > prev ? close - 10 atr : close + 10 atr  (prev = nz(stop[1]))
    buy = close > stop and crossover(ema(close, 1), stop) -> entry UTBotBuy;  sell = close < stop and crossover(stop, ema(close, 1)) -> entry UTBotSell

Interpretation choices (Pine rules in SURVEY_README.md)
    * ema(close, 1) is the close itself. The trailing line starts from zero history (nz), as written.
      The other inputs feed nothing. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR trailing line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND435835 (2 members, best partner #435835, Jaccard 0.729); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439710_ut_bot_atr_trail_cross"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "a": [10, 2],
    "c": [10, 14],
}
DEFAULT_PARAMS = {"a": 10, "c": 10}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    loss = (float(p["a"]) * _atr(bars_df, p["c"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ts = np.full(m, np.nan)
    for i in range(m):
        prev = ts[i - 1] if i > 0 and not np.isnan(ts[i - 1]) else 0.0
        c1 = cv[i - 1] if i > 0 else np.nan
        if cv[i] > prev and c1 > prev:
            ts[i] = max(prev, cv[i] - loss[i])
        elif cv[i] < prev and c1 < prev:
            ts[i] = min(prev, cv[i] + loss[i])
        elif cv[i] > prev:
            ts[i] = cv[i] - loss[i]
        else:
            ts[i] = cv[i] + loss[i]
    t = pd.Series(ts, index=c.index)
    above = (c > t) & (c.shift(1) <= t.shift(1))
    below = (t > c) & (t.shift(1) <= c.shift(1))
    false = pd.Series(False, index=c.index)
    return (c > t) & above, false, (c < t) & below, false.copy()


def portfolio_kwargs(**params):
    return {}
