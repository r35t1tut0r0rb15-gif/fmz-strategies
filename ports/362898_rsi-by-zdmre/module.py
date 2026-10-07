"""RSI by zdmre: RSI crossing up into overbought (above 70) goes LONG and crossing down into
oversold (below 30) goes SHORT, as written (always in).
Port of FMZ strategy #362898 "RSI by zdmre".

Source
    https://www.fmz.com/strategy/362898 (PineScript v5, FMZ last modified 2022-05-13 16:47:24).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 50-70), RSI 14 on close
    rsi = down == 0 ? 100 : up == 0 ? 0 : 100 - 100 / (1 + up / down)
    ob = cross(rsi, 70) and rsi >= 70;  os = cross(rsi, 30) and rsi <= 30
    ob -> entry "Enter Long"; else os -> entry "Enter Short"

Interpretation choices (Pine rules in SURVEY_README.md)
    * cross() with rsi >= 70 can only be the upward cross (rsi > 70, rsi[1] <= 70); os is the
      downward cross through 30.
    * Entering long on the overbought cross (and short on oversold) is kept as written.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362898_rsi_extreme_cross_momentum"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [7, 14, 21],
}
DEFAULT_PARAMS = {"rsi_len": 14, "upper": 70.0, "lower": 30.0}


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


def _rsi_pine(close, n):
    d = close.diff()
    up, down = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = 100.0 - 100.0 / (1.0 + up / down)
    return rsi.mask(up == 0, 0.0).mask(down == 0, 100.0).where(up.notna() & down.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    rsi = _rsi_pine(bars_df["close"], int(p["rsi_len"]))
    r1 = rsi.shift(1)
    ob = ((rsi > p["upper"]) & (r1 <= p["upper"])).to_numpy()
    os_ = ((rsi < p["lower"]) & (r1 >= p["lower"])).to_numpy()
    return _always_in(ob, os_, bars_df.index)


def portfolio_kwargs(**params):
    return {}
