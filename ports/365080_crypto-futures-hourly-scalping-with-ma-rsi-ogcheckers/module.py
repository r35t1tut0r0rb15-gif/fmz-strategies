"""ogcheckers scalp: after a green bar, a red bar that opens at or below the previous close and
closes at or below it, with RSI(open, 7) at or above 80, goes long; the same candle pattern with
RSI(open, 7) at or above 75 (but below 80) goes short, as written (always in).
Port of FMZ strategy #365080 "ogcheckers_1hr_scalp_ema_sma_rsi".

Source
    https://www.fmz.com/strategy/365080 (PineScript v5, FMZ last modified 2022-05-23 14:25:26).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 46-141), RSI upper 75, buffer 5
    pattern = close[1] >= open[1] and close[1] >= open and open >= close and close[1] >= close
    pattern and rsi(open, 7) >= 75 + 5 -> entry long
    else pattern and rsi(open, 7) >= 75 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The EMA/SMA flags and all daily request.security values are computed but never reach the
      orders; not ported (so no higher-timeframe read is needed).
    * The order lines use RSI(7) whatever the rsi_length input says, as coded.
    * The long/short mapping (higher RSI -> long) is kept as written.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "10min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365080_red_bar_rsi_extreme"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_upper": [70, 75],
    "rsi_buffer": [5, 10],
}
DEFAULT_PARAMS = {"rsi_upper": 75, "rsi_buffer": 5}


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
    o, c = bars_df["open"], bars_df["close"]
    pat = ((c.shift(1) >= o.shift(1)) & (c.shift(1) >= o) & (o >= c) & (c.shift(1) >= c)).to_numpy()
    r7 = _rsi(o, 7).to_numpy()
    long_ = pat & (r7 >= p["rsi_upper"] + p["rsi_buffer"])
    short = pat & ~long_ & (r7 >= p["rsi_upper"])
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
