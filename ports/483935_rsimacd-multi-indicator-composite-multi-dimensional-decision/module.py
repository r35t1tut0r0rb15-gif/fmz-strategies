"""2-hour bars: at least 3 of 5 bullish readings (RSI 18 under 30, MACD over its signal, close inside the Bollinger bands (20, 2.5), volume above its 20-bar average, close above the SMA 50) go long; at least 3 of the 5 bearish readings go short; the opposite signal reverses.
Port of FMZ strategy #483935 "多指标合成多维决策交易系统-基于RSIMACD布林带成交量及趋势的量化策略-Multi-Indicator-Composite-Multi-Dimensional-Decision-Trading-System-A-Quantitative-Strategy-Based-on-RSI-MACD-Bollinger-Bands-Volume-and-Trend" (3/5 Indicator Strategy with Table).

FMZ source id: 483935

Source
    https://www.fmz.com/strategy/483935 (PineScript v6, FMZ last modified 2025-02-27 09:41:04).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 206-301), RSI 18; MACD 12 / 26 / 9; BB 20 x 2.5; volume SMA 20; SMA 50; vote >= 3; 15 % of equity
    bullishSignals = (rsi < 30) + (macd > signal) + (lowerBB < close < upperBB) + (volume > sma(volume, 20)) + (close > sma50);  >= 3 -> entry Long
    bearishSignals = (rsi > 70) + (macd < signal) + (close < lowerBB) + (volume < sma(volume, 20)) + (close < sma50);  >= 3 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bullish and bearish items are exclusive pairs, so both votes can never reach 3 together. The
      "bullish" Bollinger item is simply a close inside the bands, as written. The votes are states;
      entries only, an opposite entry reverses. The status table only displays. REVERSAL INTENDED. 15 %
      of equity and the commission are sizing and costs. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, five-indicator vote.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 15 % of equity and commission stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20 in both votes; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483935_five_indicator_vote_3of5_2h_reversal"
FAMILY = "indicator_vote"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "need": [3, 4],
    "rsi_len": [18, 14],
}
DEFAULT_PARAMS = {"need": 3, "rsi_len": 18, "bb_mult": 2.5}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    basis, dev = c.rolling(20).mean(), float(p["bb_mult"]) * c.rolling(20).std(ddof=0)
    up_b, lo_b = basis + dev, basis - dev
    vma = v.rolling(20).mean()
    s50 = c.rolling(50).mean()
    bull = ((r < 30).astype(int) + (macd > sig).astype(int) + ((c > lo_b) & (c < up_b)).astype(int)
            + (v > vma).astype(int) + (c > s50).astype(int))
    bear = ((r > 70).astype(int) + (macd < sig).astype(int) + (c < lo_b).astype(int)
            + (v < vma).astype(int) + (c < s50).astype(int))
    k = int(p["need"])
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (bull >= k).astype(bool), false, (bear >= k).astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
