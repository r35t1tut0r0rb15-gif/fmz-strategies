"""EMA 20 / 50 crossings with an EMA 200 filter, 1-hour bars: the cross up above the EMA 200 goes long, the cross down below it short; the opposite crossing closes; reversing.
Port of FMZ strategy #443135 "基于EMA和ATRRSI过滤器的趋势跟踪策略An-Advanced-EMA-Trend-Following-Strategy-with-Relaxed-RSI-and-ATR-Filters" (EMA Strategy with Trend Filter).

FMZ source id: 443135

Source
    https://www.fmz.com/strategy/443135 (PineScript v5, FMZ last modified 2024-02-29 14:44:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 111-162), EMA 20 / 50 / 200; RSI 14 and ATR 14 (plots only)
    crossover(ema20, ema50) and close > ema200 -> entry Buy;  crossunder and close < ema200 -> entry Sell;  crossunder -> close Buy;  crossover -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSI and ATR only plot. Ported in call order with one position at a time; each close acts only
      on a held position. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with a trend filter.
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

NAME = "fmz_443135_ema20_50_cross_ema200_filter_cross_exits"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_ema": [20, 10],
    "long_ema": [50, 100],
}
DEFAULT_PARAMS = {"short_ema": 20, "long_ema": 50, "trend_ema": 200}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s = c.ewm(span=int(p["short_ema"]), adjust=False).mean()
    l_ = c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    t = c.ewm(span=int(p["trend_ema"]), adjust=False).mean()
    up = ((s > l_) & (s.shift(1) <= l_.shift(1))).to_numpy()
    dn = ((s < l_) & (s.shift(1) >= l_.shift(1))).to_numpy()
    above, below = (c > t).to_numpy(), (c < t).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if up[i] and above[i] and new != 1:
            new = 1
        if dn[i] and below[i] and new != -1:
            new = -1
        if dn[i] and held == 1 and new == 1:
            new = 0
        if up[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
