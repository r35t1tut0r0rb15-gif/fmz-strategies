"""PresentTrend (an AlphaTrend-style ratcheting low - 1.618 ATR 14 / high + 1.618 ATR 14 line switched by MFI 14 of hlc3 at 50), 2-hour bars: the line crossing over its value two bars back, with the previous buy older than the last sell, turns the trend up and goes long; the mirror turns it down and goes short; reversing.
Port of FMZ strategy #427466 "PresentTrend趋势跟随策略PresentTrend-Trend-Following-Strategy" (PresentTrend - Strategy [presentTrading]).

FMZ source id: 427466

Source
    https://www.fmz.com/strategy/427466 (PineScript v5, FMZ last modified 2023-09-21 15:00:08).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 136-186), length 14, multiplier 1.618; ATR = sma(tr, 14); MFI(hlc3, 14) (RSI switch off); direction Both
    PresentTrend := mfi(hlc3, 14) >= 50 ? (low - atr x 1.618 < PT[1] ? PT[1] : low - atr x 1.618) : (high + atr x 1.618 > PT[1] ? PT[1] : high + atr x 1.618)
    longSignal = crossover(PT, PT[2]);  trendDirection := longSignal and barssince(longSignal[1]) > barssince(shortSignal) ? 1 : shortSignal and barssince(shortSignal[1]) > barssince(longSignal) ? -1 : trendDirection[1];  1 -> entry Buy, -1 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line starts from nz(PT[1]) = 0 and ratchets as written (the AlphaTrend of #377541 with a 1.618
      multiplier). The direction keeps its last value and is na (no trade) before its first signal; a
      barssince with no event yet is na and its comparison is false. The entries are sent every bar of a
      direction (repeats ignored). ta.mfi as Pine defines it. REVERSAL INTENDED. The 10 % of equity size,
      slippage and commission are sizing / costs. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MFI-switched ATR trailing line against its own lag, with alternation filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity, capital 10000, commission 0.1 %, slippage 1 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in ta.mfi(hlc3, 14); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427466_presenttrend_mfi14_atr1618_line_lag2_alternating_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "multiplier": [1.618, 1.0],
}
DEFAULT_PARAMS = {"length": 14, "multiplier": 1.618}


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


def _mfi(src, vol, n):
    """Pine ta.mfi: money-flow ratio over n bars; 100 when the falling flow is 0, 0 when the rising is 0."""
    ch = src.diff()
    upper = (vol * src.where(~(ch <= 0), 0.0)).rolling(n).sum()
    lower = (vol * src.where(~(ch >= 0), 0.0)).rolling(n).sum()
    out = 100.0 - 100.0 / (1.0 + upper / lower.where(lower != 0))
    return out.where(upper != 0, 0.0).where(lower != 0, 100.0).where(upper.notna() & lower.notna())


def _barssince(cond):
    """Pine barssince: bars since cond was last true (NaN before the first true)."""
    a = np.asarray(cond, dtype=bool)
    idx = np.maximum.accumulate(np.where(a, np.arange(len(a)), -1))
    return np.where(idx >= 0, np.arange(len(a)) - idx, np.nan)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    n, k = int(p["length"]), float(p["multiplier"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = tr.rolling(n).mean()
    up_t, dn_t = (lo - atr * k).to_numpy(dtype=float), (h + atr * k).to_numpy(dtype=float)
    bull = (_mfi((h + lo + c) / 3, v, n) >= 50).to_numpy()
    m = len(up_t)
    pt = np.zeros(m)
    prev = 0.0
    for i in range(m):
        if bull[i]:
            pt[i] = prev if up_t[i] < prev else up_t[i]
        else:
            pt[i] = prev if dn_t[i] > prev else dn_t[i]
        prev = 0.0 if np.isnan(pt[i]) else pt[i]
    pts = pd.Series(pt, index=c.index)
    p2 = pts.shift(2)
    ls = ((pts > p2) & (pts.shift(1) <= p2.shift(1))).to_numpy()
    ss = ((pts < p2) & (pts.shift(1) >= p2.shift(1))).to_numpy()
    bs_buy, bs_sell = _barssince(ls), _barssince(ss)
    prev_buy = _barssince(np.r_[False, ls[:-1]])
    prev_sell = _barssince(np.r_[False, ss[:-1]])
    td = np.zeros(m)
    d = 0.0
    for i in range(m):
        if ls[i] and prev_buy[i] > bs_sell[i]:
            d = 1.0
        elif ss[i] and prev_sell[i] > bs_buy[i]:
            d = -1.0
        td[i] = d
    le = pd.Series(td == 1, index=c.index)
    se = pd.Series(td == -1, index=c.index)
    return le, pd.Series(False, index=c.index), se, pd.Series(False, index=c.index)


def portfolio_kwargs(**params):
    return {}
