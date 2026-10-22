"""Alternating MACD crossings at the Bollinger 20 / 2 edges, 3-hour bars: a MACD cross up with the RSI under 45 and the close under 102 % of the lower band goes long, a MACD cross down with the RSI over 55 and the close over 98 % of the upper band goes short; the sides alternate (the first is a long) and at least 15 bars separate trades; reversing.
Port of FMZ strategy #471671 "结合布林带与RSI的自适应震荡趋势交易策略-Adaptive-Oscillation-Trend-Trading-Strategy-with-Bollinger-Bands-and-RSI-Integration" ([ETH] Optimized Trend Strategy (Lorenzo-SuperScalping)).

FMZ source id: 471671

Source
    https://www.fmz.com/strategy/471671 (PineScript v5, FMZ last modified 2024-11-12 11:35:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-179), RSI 14; BB 20, 2 sd; MACD 12 / 26 / 9; minimum 15 bars between trades; last_signal_buy flag; trade size 1 ETH; pyramiding 3
    rsi < 45 and close < lower x 1.02 and crossover(macd, signal) and last signal not a buy and 15 bars passed -> (close Short) entry Long, last = buy
    rsi > 55 and close > upper x 0.98 and crossunder(macd, signal) and last signal a buy and 15 bars passed -> (close Long) entry Short, last = sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The last-signal flag starts as na, so the first trade must be a long, and the sides then
      alternate, so pyramiding 3 never adds. The bar counter starts at the first trade. Each close plus
      the opposite entry is a reversal. There is no other exit. The 1-ETH size is not ported; the title
      names ETH, the rules are generic. REVERSAL INTENDED. FREQ = "3h" from the backtest header
      (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings at the band edges, alternating with a bar gap.
    3 crypto-exchange-only: no (exchange pair in the header only (ETH named in the title)).
    4 signals only: fixed trade size stored, not ported.
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

NAME = "fmz_471671_alternating_macd_cross_band_edges_bar_gap_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "min_gap": [15, 5],
    "bb_length": [20, 50],
}
DEFAULT_PARAMS = {"min_gap": 15, "bb_length": 20, "bb_mult": 2.0, "rsi_length": 14}


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
    r = _rsi(c, int(p["rsi_length"]))
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = c.rolling(n).std(ddof=0) * float(p["bb_mult"])
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    buy = ((r < 45) & (c < (basis - dev) * 1.02) & (macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    sell = ((r > 55) & (c > (basis + dev) * 0.98) & (macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    gap = int(p["min_gap"])
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last_buy, last_bar = None, None
    for i in range(m):
        elapsed = last_bar is None or i - last_bar >= gap
        if buy[i] and last_buy is not True and elapsed:
            le[i], last_buy, last_bar = True, True, i
        if sell[i] and last_buy is True and elapsed:
            se[i], last_buy, last_bar = True, False, i
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
