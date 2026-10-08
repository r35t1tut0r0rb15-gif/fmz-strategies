"""BB + Stochastic RSI extreme: a close coming back inside the upper band after an extreme stoch-RSI
(> 90) goes LONG; a close coming back inside the lower band after stoch-RSI < 10 goes SHORT, as
written (always in).
Port of FMZ strategy #366946 "Bollinger Bands Stochastic RSI Extreme Signal".

Source
    https://www.fmz.com/strategy/366946 (PineScript v4, FMZ last modified 2022-05-31 19:16:17).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 65-119), BB 20 x 2, stoch RSI 14 / 14 / 3 / 3, 90 / 10
    Bear = close[1] > upper[1] and close < upper and k[1] > 90 and d[1] > 90
    Bull = close[1] < lower[1] and close > lower and k[1] < 10 and d[1] < 10
    Bear -> entry "Enter Long"; else Bull -> entry "Enter Short"

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are inverted relative to the signal names; kept as written.
    * Population stdev. strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "15min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366946_bb_stochrsi_extreme_inverse"
FAMILY = "bollinger_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "mult": [1.5, 2.0],
    "limit": [80, 90],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "rsi_len": 14, "stoch_len": 14, "k": 3, "d": 3, "limit": 90}


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
    c = bars_df["close"]
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper, lower = basis + p["mult"] * sd, basis - p["mult"] * sd
    rsi = _rsi(c, int(p["rsi_len"]))
    s = int(p["stoch_len"])
    st = 100 * (rsi - rsi.rolling(s).min()) / (rsi.rolling(s).max() - rsi.rolling(s).min())
    k = st.rolling(int(p["k"])).mean()
    d = k.rolling(int(p["d"])).mean()
    hi, lo = p["limit"], 100 - p["limit"]
    bear = ((c.shift(1) > upper.shift(1)) & (c < upper) & (k.shift(1) > hi) & (d.shift(1) > hi)).to_numpy()
    bull = ((c.shift(1) < lower.shift(1)) & (c > lower) & (k.shift(1) < lo) & (d.shift(1) < lo)).to_numpy()
    return _always_in(bear, bull, bars_df.index)


def portfolio_kwargs(**params):
    return {}
