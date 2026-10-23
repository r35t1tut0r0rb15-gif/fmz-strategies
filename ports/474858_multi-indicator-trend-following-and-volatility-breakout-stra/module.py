"""2-hour bars, long only: above the EMA 50 above the EMA 200 with the script's ADX 14 over 25, the close above Ichimoku span A and the stochastic 14 under 20 it goes long; the mirror set-up (below span B, stochastic over 80) closes the long.
Port of FMZ strategy #474858 "Multi Indicator Trend Following and Volatility Breakout Strategy" (Khaleq Strategy Pro - Fixed Version).

FMZ source id: 474858

Source
    https://www.fmz.com/strategy/474858 (PineScript v5, FMZ last modified 2024-12-12 15:48:29).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 133-246), EMA 50 / 200; manual ADX 14 (SMAs) > 25; Ichimoku 9 / 26 / 52 (undisplaced); stoch 14; ATR 14 x 2
    buy_signal = close > ema50 and ema50 > ema200 and adx > 25 and close > senkou_span_a and k < 20 -> entry Buy
    sell_signal = close < ema50 and ema50 < ema200 and adx > 25 and close < senkou_span_b and k > 80 -> close Buy, exit("Sell", "Buy", stop = close - 2 atr, limit = close + 2 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The sell bar closes the long at the next open; the bracket sent with it is not followed (the close
      ends the trade first; on a flat sell bar it would wait for a later "Buy", which is not modelled).
      The ADX uses SMAs of max(change(high), 0), max(-change(low), 0) and the true range (moves not
      compared). The spans are compared undisplaced, as written; the time filter is always true; OBV
      only plots (held for volume, not used). A buy and a sell never meet on one bar. Long only. No
      sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic dips in an EMA / Ichimoku uptrend with ADX strength.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474858_ema_ichimoku_adx_stoch_dip_2h_long_only"
FAMILY = "trend_pullback"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_min": [25.0, 20.0],
    "k_low": [20.0, 30.0],
}
DEFAULT_PARAMS = {"adx_min": 25.0, "k_low": 20.0, "k_high": 80.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    mid = lambda n: (h.rolling(n).max() + lo.rolling(n).min()) / 2
    span_a = (mid(9) + mid(26)) / 2
    span_b = mid(52)
    e50, e200 = c.ewm(span=50, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    tr14 = tr.rolling(14).mean()
    dip = h.diff().clip(lower=0).rolling(14).mean() / tr14 * 100
    dim = (-lo.diff()).clip(lower=0).rolling(14).mean() / tr14 * 100
    adx = ((dip - dim).abs() / (dip + dim) * 100).rolling(14).mean()
    ll, hh = lo.rolling(14).min(), h.rolling(14).max()
    k = 100 * (c - ll) / (hh - ll)
    strong = adx > float(p["adx_min"])
    buy = (c > e50) & (e50 > e200) & strong & (c > span_a) & (k < float(p["k_low"]))
    sell = (c < e50) & (e50 < e200) & strong & (c < span_b) & (k > float(p["k_high"]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), sell.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
