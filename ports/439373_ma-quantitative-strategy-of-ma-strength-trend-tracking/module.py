"""EMA alignment score against its Hull average, long only, 1-hour bars: a 10-bar sum of points for the close above the EMA 5 and each EMA (5 to 200) above the next crossing over its HMA 200 while rising goes
long; crossing under it while falling closes.
Port of FMZ strategy #439373 "量化策略之MA强弱趋势追踪Quantitative-Strategy-of-MA-Strength-Trend-Tracking" (MA Strength Strategy).

FMZ source id: 439373

Source
    https://www.fmz.com/strategy/439373 (PineScript v4, FMZ last modified 2024-01-19 16:50:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 119-191), MA type ema; lookback 10; index MA hma 200; trend direction for entry and exit on; offset 1; trade direction long; date range true
    upwardScore = 1.10 (close > ema5) + 1.10 (ema5 > ema10) + 1.10 (ema10 > ema20) + 1.10 (ema20 > ema30) + 1.15 (ema30 > ema50) + 1.20 (ema50 > ema100) + 1.25 (ema100 > ema200);  upwardSum = sum(upwardScore, 10)
    buy = crossover(upwardSum, hma(upwardSum, 200)) and upwardSum > upwardSum[1];  sell = crossunder and upwardSum < upwardSum[1];  entry Buy;  close Buy on sell;  entry Sell on sell (long direction only)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.risk.allow_entry_in(long) blocks the short entry and turns it into a close of the long,
      the same bar as the written close; the short close does nothing. The HMA uses length / 2 and the
      rounded square root. Long only. The 100 % of equity size and the commission are sizing. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA alignment score and its HMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439373_ema_alignment_score_hma_cross_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [10, 20],
    "index_period": [200, 100],
}
DEFAULT_PARAMS = {"lookback": 10, "index_period": 200, "offset": 1}

LADDER = ((5, 10, 1.10), (10, 20, 1.10), (20, 30, 1.10), (30, 50, 1.15), (50, 100, 1.20), (100, 200, 1.25))


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(src, n):
    return _wma(2 * _wma(src, n // 2) - _wma(src, n), int(round(np.sqrt(n))))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e = {n: c.ewm(span=n, adjust=False).mean() for n in (5, 10, 20, 30, 50, 100, 200)}
    score = 1.10 * (c > e[5])
    for a, b, w in LADDER:
        score = score + w * (e[a] > e[b])
    s = score.rolling(int(p["lookback"])).sum()
    idx = _hma(s, int(p["index_period"]))
    k = int(p["offset"])
    buy = (s > idx) & (s.shift(1) <= idx.shift(1)) & (s > s.shift(k))
    sell = (s < idx) & (s.shift(1) >= idx.shift(1)) & (s < s.shift(k))
    false = pd.Series(False, index=c.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
