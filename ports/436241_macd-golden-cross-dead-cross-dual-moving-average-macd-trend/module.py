"""Triple average crossing with a MACD filter, 15-minute bars: the EMA 5 crossing over both the WMA 85 and the WMA 75 of lows on one bar with a positive MACD histogram goes long; the mirror goes
short (reversing); each trade has a tick-sized stop and target re-expressed as ATR multiples.
Port of FMZ strategy #436241 "金叉死叉双均线MACD趋势追踪策略Golden-Cross-Dead-Cross-Dual-Moving-Average-MACD-Trend-Tracking-Strategy" (The Puria Method).

FMZ source id: 436241

Source
    https://www.fmz.com/strategy/436241 (PineScript v2, FMZ last modified 2023-12-22 14:17:34).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 157-204), EMA 5 of close; WMA 85 / 75 of low; MACD 12 / 26 / 9; take profit 30, stop 10, trail 5 (ticks)
    signalUp = crossover(ema5, wma85(low)) and crossover(ema5, wma75(low)) and hist > 0;  signalDown = the mirror with hist < 0;  entry long / short;  exit(profit = 30, loss = 10, trail_points = 5, trail_offset = na)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the tick amounts (30 / 10 ticks) are re-expressed as sl_stop = k_atr x ATR / close
      and tp_stop = 3 x sl_stop of the signal bar, shifted one bar inside stops() (re-based on the fill);
      0.0125 is the reading (1 USD on BTC against a 15-minute ATR near 80), 0.5 a volatility-sized stop.
      trail_points without a trail_offset starts no trailing stop. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 15-minute bars: not coarse. FREQ = "15min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick amounts -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick inputs quoted in original_sizing.txt.
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

NAME = "fmz_436241_triple_ma_cross_macd_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [0.0125, 0.5],
    "slow1": [85, 60],
}
DEFAULT_PARAMS = {"k_atr": 0.0125, "slow1": 85, "slow2": 75, "fast": 5, "tp_ratio": 3.0, "atr_len": 14}


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


def _wma(s, n):
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return s.rolling(n).apply(lambda a: float(np.dot(a, w) / w.sum()), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lo, c = bars_df["low"], bars_df["close"]
    fast = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s1, s2 = _wma(lo, p["slow1"]), _wma(lo, p["slow2"])
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))      # noqa: E731
    xu = lambda a, b: (a < b) & (a.shift(1) >= b.shift(1))      # noqa: E731
    le = (xo(fast, s1) & xo(fast, s2) & (hist > 0)).fillna(False).astype(bool)
    se = (xu(fast, s1) & xu(fast, s2) & (hist < 0)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    f = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["k_atr"])).shift(1)
    return {"sl_stop": f, "tp_stop": f * float(p["tp_ratio"])}


def portfolio_kwargs(**params):
    return {}
