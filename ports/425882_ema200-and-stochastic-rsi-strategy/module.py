"""EMA 200 + stochastic RSI: above EMA 200, a stoch-RSI %K cross above %D below 20 on a strong green
bar (higher high, after a green bar, small upper wick, >= 0.5 % gain) goes long; the mirror goes
short (always in).
Port of FMZ strategy #425882 "EMA200 and Stochastic RSI Strategy".

Source
    https://www.fmz.com/strategy/425882 (PineScript v5, FMZ last modified 2023-09-06 11:28:53).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 80-115), stoch RSI 14 / 14 / 3 / 3, wick 20 %, change 0.5 %
    long  = close > ema200 and k < 20 and d < 20 and crossover(k, d) and high > high[1]
            and close[1] > open[1] and close > open and (high - close) / (high - low) <= 0.20
            and close / open - 1 >= 0.005
    short = close < ema200 and k > 80 and d > 80 and crossunder(k, d) and low < low[1]
            and close[1] < open[1] and close < open and |high - open| / |high - close| <= 0.20
            and 1 - close / open >= 0.005
    long -> entry long; else short -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short wick test |high - open| / |high - close| is kept as written (not the mirror of
      the long one). The ATR stop lines and the reward/risk input only draw.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_425882_ema200_stochrsi_strong_bar"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "wick_pct": [20, 40],
    "change_pct": [0.25, 0.5],
    "ema_len": [100, 200],
}
DEFAULT_PARAMS = {"wick_pct": 20, "change_pct": 0.5, "ema_len": 200}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


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
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    rsi = _rsi(c, 14)
    st = 100 * (rsi - rsi.rolling(14).min()) / (rsi.rolling(14).max() - rsi.rolling(14).min())
    k = st.rolling(3).mean()
    d = k.rolling(3).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    w, ch = p["wick_pct"] / 100, p["change_pct"] / 100
    long_ = ((c > ema) & (k < 20) & (d < 20) & (k > d) & (k.shift(1) <= d.shift(1)) & (h > h.shift(1))
             & (c.shift(1) > o.shift(1)) & (c > o) & ((h - c) / (h - l) <= w) & (c / o - 1 >= ch))
    short = ((c < ema) & (k > 80) & (d > 80) & (k < d) & (k.shift(1) >= d.shift(1)) & (l < l.shift(1))
             & (c.shift(1) < o.shift(1)) & (c < o) & ((h - o).abs() / (h - c).abs() <= w) & (1 - c / o >= ch))
    return _always_in(long_.to_numpy(), short.to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
