"""SMA / EMA with stochastic (always in): the close crossing above SMA 50 with %K and %D above 50
goes long; the close crossing under EMA 25 with %K and %D below 80 goes short.
Port of FMZ strategy #426482 "Stoch Dual MA Stoch Indicators Combo Trading Strategy".

Source
    https://www.fmz.com/strategy/426482 (PineScript v4, FMZ last modified 2023-09-12 14:44:56).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 119-189), MA 50, EMA 25, stoch 20 / 2 / 2, 50 / 80
    k = sma(stoch(close, high, low, 20), 2); d = sma(k, 2)
    crossover(close, sma(close, 50)) and k > 50 and d > 50   -> entry long
    crossunder(close, ema(close, 25)) and k < 80 and d < 80  -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * InTime is hard-coded true (the test-year inputs are unused). The long / short / trade flags
      only colour the background.
    * If both entries fire on one bar, both orders fill at the next open in source order and the
      later (short) one stands: the short is taken (short_first).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426482_ma_stoch_combo"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "l_ma": [50, 100],
    "l_ema": [25, 50],
    "stk_long": [50, 60],
}
DEFAULT_PARAMS = {"l_ma": 50, "l_ema": 25, "length": 20, "smooth_k": 2, "smooth_d": 2,
                  "stk_long": 50, "stk_short": 80}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ma = c.rolling(int(p["l_ma"])).mean()
    ema = c.ewm(span=int(p["l_ema"]), adjust=False).mean()
    n = int(p["length"])
    lo, hi = l.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - lo) / (hi - lo)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    c1 = c.shift(1)
    long_ = ((c > ma) & (c1 <= ma.shift(1)) & (k > p["stk_long"]) & (d > p["stk_long"])).to_numpy()
    short = ((c < ema) & (c1 >= ema.shift(1)) & (k < p["stk_short"]) & (d < p["stk_short"])).to_numpy()
    return _always_in(long_, short, bars_df.index, short_first=True)


def portfolio_kwargs(**params):
    return {}
