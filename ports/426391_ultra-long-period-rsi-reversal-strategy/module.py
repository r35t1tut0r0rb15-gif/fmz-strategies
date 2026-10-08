"""RSI(65) 40 / 60 reversal (always in): RSI crossing above 40 goes long, crossing under 60 goes
short.
Port of FMZ strategy #426391 "Ultra Long Period RSI Reversal Strategy".

Source
    https://www.fmz.com/strategy/426391 (PineScript v3, FMZ last modified 2023-09-11 17:36:19).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 64-75), length 65, 40 / 60
    crossover(rsi(close, 65), 40) -> entry long;  crossunder(rsi, 60) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426391_rsi65_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [30, 65, 100],
    "band": [10, 15],
}
DEFAULT_PARAMS = {"length": 65, "band": 10}  # oversold 50 - band, overbought 50 + band


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


def _rsi_pine(close, n):
    """rsi() as Pine defines it: 100 when the average loss is 0, 0 when the average gain is 0."""
    d = close.diff()
    up, down = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = 100.0 - 100.0 / (1.0 + up / down)
    return rsi.mask(up == 0, 0.0).mask(down == 0, 100.0).where(up.notna() & down.notna())


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
    r = _rsi_pine(bars_df["close"], int(p["length"]))
    r1 = r.shift(1)
    lo, hi = 50 - p["band"], 50 + p["band"]
    long_ = ((r > lo) & (r1 <= lo)).to_numpy()
    short = ((r < hi) & (r1 >= hi)).to_numpy()
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
