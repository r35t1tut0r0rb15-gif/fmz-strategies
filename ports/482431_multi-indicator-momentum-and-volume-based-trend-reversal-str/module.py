"""Hourly bars: a MACD crossing over its signal with RSI 14 under 40, the close under an EMA 100 range band (3 x the double-smoothed average move) and above-average volume goes long; the mirror (RSI over 80, close over the upper band) goes short; the opposite signal reverses.
Port of FMZ strategy #482431 "Multi Indicator Momentum and Volume Based Trend Reversal Strategy" (MACD & RSI with Range and Volume Filter).

FMZ source id: 482431

Source
    https://www.fmz.com/strategy/482431 (PineScript v6, FMZ last modified 2025-02-18 14:04:30).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 112-177), MACD 12 / 26 / 9; RSI 14 (80 / 40); range filter EMA 100, smoothed range EMA 100 then EMA 199, x 3; volume SMA 20
    smoothedRange = ema(ema(abs(close - close[1]), 100), 199) x 3;  bands = ema(close, 100) +- smoothedRange
    buyCondition = crossover(macd, signal) and rsi < 40 and close < lowerBand and volume > sma(volume, 20) -> entry Buy;  sellCondition mirrored (rsi > 80, close > upperBand) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries only; an opposite entry reverses. Both set-ups are rare (a MACD bullish crossing far below
      the band with RSI under 40, and the mirror with RSI over 80). REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings at range-band extremes with RSI and volume filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
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

NAME = "fmz_482431_macd_cross_rsi_range_band_extreme_volume_1h_reversal"
FAMILY = "macd"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "range_mult": [3.0, 2.0],
    "rsi_lo": [40.0, 30.0],
}
DEFAULT_PARAMS = {"range_len": 100, "range_mult": 3.0, "rsi_lo": 40.0, "rsi_hi": 80.0}


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
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, 14)
    n = int(p["range_len"])
    rng = c.diff().abs().ewm(span=n, adjust=False).mean().ewm(span=2 * n - 1, adjust=False).mean() * float(p["range_mult"])
    mid = c.ewm(span=n, adjust=False).mean()
    vol_ok = v > v.rolling(20).mean()
    buy = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (r < float(p["rsi_lo"])) & (c < mid - rng) & vol_ok
    sell = (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (r > float(p["rsi_hi"])) & (c > mid + rng) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
