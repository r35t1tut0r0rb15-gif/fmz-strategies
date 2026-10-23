"""Hourly bars: a green bar on above-average volume closing over the previous 5-bar high, with the MACD above its signal and above 0, while the bar overlaps the last stored fair-value gap, goes long; the bearish mirror goes short; reversing.
Port of FMZ strategy #484089 "多维度量化交易系统高级VSA-MACD-FVG策略分析与优化框架-Advanced-Quantitative-Trading-System-VSA-MACD-FVG-Strategy-Analysis-and-Optimization-Framework" (VSA_MACD_FVG Strategy).

FMZ source id: 484089

Source
    https://www.fmz.com/strategy/484089 (PineScript v5, FMZ last modified 2025-02-28 09:39:23).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 179-243), MACD 12 / 26 / 9; VSA (volume SMA 20, 5-bar extreme [1]); FVG low > high[2] (with a green middle bar) stored in var levels
    vsaBullish = close > open and volume > sma(volume, 20) and close > highest(high, 5)[1];  FVG up: low > high[2] and close[1] > open[1] -> fvgTop := low, fvgBottom := high[2] (down mirrored)
    buySignal = vsaBullish and macd > signal and macd > 0 and high >= fvgBottom and low <= fvgTop and not long -> entry Buy;  sellSignal mirrored and not short -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The gap levels start at 0 (so no bar overlaps them until the first gap) and keep the latest gap
      until a new one; a bar that makes a gap always overlaps it. The entries skip the side already held;
      an opposite entry reverses. The header names TRUMP_USDT; the rules are generic. REVERSAL INTENDED.
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume-spread breakouts with MACD momentum inside fair-value gaps.
    3 crypto-exchange-only: no (exchange pair in the header only (TRUMP_USDT)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_484089_vsa_macd_fvg_overlap_1h_reversal"
FAMILY = "gap"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "price_lb": [5, 10],
    "fvg_lb": [2, 3],
}
DEFAULT_PARAMS = {"price_lb": 5, "fvg_lb": 2, "vsa_shift": 1}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _fvg_signals(bars_df, p):
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    vol_ok = v > v.rolling(20).mean()
    n, s, g = int(p["price_lb"]), int(p["vsa_shift"]), int(p["fvg_lb"])
    vsa_b = (c > o) & vol_ok & (c > h.rolling(n).max().shift(s))
    vsa_s = (c < o) & vol_ok & (c < lo.rolling(n).min().shift(s))
    up = ((lo > h.shift(g)) & (c.shift(1) > o.shift(1))).to_numpy()
    dn = ((h < lo.shift(g)) & (c.shift(1) < o.shift(1))).to_numpy()
    hn, ln = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    hg, lg = h.shift(g).to_numpy(dtype=float), lo.shift(g).to_numpy(dtype=float)
    top, bot = np.zeros(len(hn)), np.zeros(len(hn))
    t = b = 0.0
    for i in range(len(hn)):
        if up[i]:
            t, b = ln[i], hg[i]
        elif dn[i]:
            t, b = lg[i], hn[i]
        top[i], bot[i] = t, b
    inside = (hn >= bot) & (ln <= top)
    buy = (vsa_b & (macd > sig) & (macd > 0)).to_numpy() & inside
    sell = (vsa_s & (macd < sig) & (macd < 0)).to_numpy() & inside
    return buy, sell


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell = _fvg_signals(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy, index=ix), false, pd.Series(sell, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
