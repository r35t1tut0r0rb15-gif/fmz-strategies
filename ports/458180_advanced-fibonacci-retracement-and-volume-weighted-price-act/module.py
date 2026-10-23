"""Hourly bars: a "pin bar" (upper wick over twice the body) or a bullish engulfing candle on volume above 1.5 x its 20-bar average goes long; a lower-wick pin bar or a bearish engulfing candle on such volume goes short, but only on every 20th bar and only when the close is under that bar's own 38.2 % retracement point; reversing.
Port of FMZ strategy #458180 "Advanced Fibonacci Retracement and Volume Weighted Price Action Trading Strategy" (Fibonacci and Price Action with Volume Strategy).

FMZ source id: 458180

Source
    https://www.fmz.com/strategy/458180 (PineScript v5, FMZ last modified 2024-07-30 16:13:37).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 164-242), fibLength 20; volume SMA 20 x 1.5; pin bar wick > 2 x body; engulfing
    fibonacciLevels = array.new_float(5, 0)  (not var: rebuilt with zeros every bar);  if bar_index % 20 == 0: fibHigh := high, fibLow := low, levels set from them
    longEntry = (isPinBar(true) or isBullishEngulfing()) and close > levels[2] and volumeCondition -> entry Buy
    shortEntry = (isPinBar(false) or isBearishEngulfing()) and close < levels[2] and volumeCondition -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The level array is not a var: it is rebuilt with zeros on every bar and filled only on bars where
      bar_index % 20 == 0, and there fibHigh / fibLow have just been reset to that bar's own high and low.
      So levels[2] is 0 on 19 bars of 20 (every long passes "close > 0", no short can pass "close < 0"),
      and on the 20th bar it is high - 0.382 x (high - low) of that same bar (weird case). bar_index is
      counted from the first bar of the data, so which bars are the 20th depends on where the data starts.
      isPinBar(true) measures the UPPER wick and isPinBar(false) the lower one, as written. The volume
      SMA uses 20 bars. Entries only; an opposite entry reverses. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pin-bar / engulfing candles on high volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458180_pin_engulf_volume_every20_fib_short_1h_reversal"
FAMILY = "candlestick_pattern"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fib_len": [20, 40],
    "vol_mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"fib_len": 20, "vol_len": 20, "vol_mult": 1.5}


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
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    body = (c - o).abs()
    pin_up = (h - np.maximum(o, c)) > body * 2
    pin_dn = (np.minimum(o, c) - lo) > body * 2
    o1, c1 = o.shift(1), c.shift(1)
    bull_e = (o1 > c1) & (c > o) & (o <= c1) & (c >= o1)
    bear_e = (c1 > o1) & (o > c) & (o >= c1) & (c <= o1)
    vol_ok = v > float(p["vol_mult"]) * v.rolling(int(p["vol_len"])).mean()
    reset = pd.Series(np.arange(len(c)) % int(p["fib_len"]) == 0, index=c.index)
    lvl = (h - 0.382 * (h - lo)).where(reset, 0.0)   # the non-var array: zeros except on reset bars
    buy = (pin_up | bull_e) & (c > lvl) & vol_ok
    sell = (pin_dn | bear_e) & (c < lvl) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
