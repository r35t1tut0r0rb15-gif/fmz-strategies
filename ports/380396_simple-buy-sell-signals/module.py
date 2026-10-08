"""Simple buy / sell signals (Zer3192): the average of SMA 21 and EMA 50 crossing above EMA 35 goes
long when RSI 9 is above 60, and goes short when RSI 9 is below 40 (both on the upward cross, as
written).
Port of FMZ strategy #380396 "Simple Buy Sell Signals".

Source
    https://www.fmz.com/strategy/380396 (PineScript v5, author Zer3192, FMZ last modified
    2022-08-28 18:30:25). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 30-52)
    ma1 = avg(sma(close, 21), ema(close, 50));  ma2 = ema(close, 35);  rsi = rsi(close, 9)
    rsiOB = rsi > 60 and not rsi[1] < 40;  rsiOS = rsi < 40 and not rsi[1] > 60
    nmL = crossover(ma1, ma2) and rsiOB -> entry long; else nmS = crossover(ma1, ma2) and rsiOS -> short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both signals use crossover (the short one is not a crossunder): kept as written.
    * The DMI values are computed but unused.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_380396_ma_cross_rsi_side"
FAMILY = "ma_trend_oscillator_pullback"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [9, 14],
    "ma2_len": [21, 35],
}
DEFAULT_PARAMS = {"rsi_len": 9, "sma_len": 21, "ema_len": 50, "ma2_len": 35}


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
    ma1 = (c.rolling(int(p["sma_len"])).mean() + c.ewm(span=int(p["ema_len"]), adjust=False).mean()) / 2
    ma2 = c.ewm(span=int(p["ma2_len"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    x = (ma1 > ma2) & (ma1.shift(1) <= ma2.shift(1))
    ob = (rsi > 60) & ~(rsi.shift(1) < 40)
    os_ = (rsi < 40) & ~(rsi.shift(1) > 60)
    return _always_in((x & ob).to_numpy(), (x & os_).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
