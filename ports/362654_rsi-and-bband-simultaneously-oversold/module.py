"""RSI and Bollinger Band at an extreme together: overbought (RSI > 70 and high above the upper
band) goes LONG, oversold (RSI < 32 and low below the lower band) goes SHORT, as written.
Port of FMZ strategy #362654 "RSI & BB'de aynı anda Oversold Yakalama".

Source
    https://www.fmz.com/strategy/362654 (PineScript v4, FMZ last modified 2022-05-12 17:48:21).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 49-88), RSI 14 (32 / 70), BB 20 x 2 on close
    bearish = rsi > 70 and high > upper;  bullish = rsi < 32 and low < lower
    bearish -> entry "Enter Long"; else bullish -> entry "Enter Short"

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are inverted relative to the condition names (bearish -> long); kept as
      written.
    * stdev is the population deviation; rsi is Wilder's.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "10min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362654_rsi_bb_extreme_inverse"
FAMILY = "bollinger_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_period": [7, 14],
    "bb_period": [20, 40],
    "bb_mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"rsi_period": 14, "rsi_low": 32, "rsi_high": 70, "bb_period": 20, "bb_mult": 2.0}


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
    n = int(p["bb_period"])
    mid = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    rsi = _rsi(c, int(p["rsi_period"]))
    bearish = ((rsi > p["rsi_high"]) & (bars_df["high"] > mid + dev)).to_numpy()
    bullish = ((rsi < p["rsi_low"]) & (bars_df["low"] < mid - dev)).to_numpy()
    return _always_in(bearish, bullish, bars_df.index)


def portfolio_kwargs(**params):
    return {}
