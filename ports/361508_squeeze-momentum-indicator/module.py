"""Squeeze-momentum histogram turns: short when a positive histogram starts falling, long when a
negative one starts rising (always in; the squeeze state itself is not used by the orders).
Port of FMZ strategy #361508 "Squeeze-Momentum-Indicator" (LazyBear SQZMOM).

Source
    https://www.fmz.com/strategy/361508 (PineScript, FMZ last modified 2022-05-08 11:17:04).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 52-91), lengthKC 14
    val = ta.linreg(close - avg(avg(highest(high,KC), lowest(low,KC)), sma(close,KC)), KC, 0)
    val > 0 and val < nz(val[1]) -> entry short
    else val < 0 and val > nz(val[1]) -> entry long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only `val` drives the orders; the Bollinger/Keltner squeeze lines feed the colours only.
    * strategy.entry reverses an opposite position: REVERSAL INTENDED (portfolio_kwargs {};
      the engine's default opposite-entry reversal applies).
    * Daily bars (backtest period 1d) are broker days (17:00 New York).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361508_squeeze_momentum_turn"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_kc": [10, 14, 20, 30],
}
DEFAULT_PARAMS = {"length_kc": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _linreg(y, n, offset=0):
    """ta.linreg(y, n, offset): least-squares line over the last n values (x = 0..n-1),
    evaluated at x = n-1-offset."""
    v = y.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        k = np.arange(n, dtype=float)
        sxy = np.convolve(v, k[::-1], mode="full")[n - 1:len(v)]   # sum_k k * v[t-n+1+k]
        sy = np.convolve(v, np.ones(n), mode="full")[n - 1:len(v)]
        slope = (n * sxy - k.sum() * sy) / (n * (k * k).sum() - k.sum() ** 2)
        intercept = (sy - slope * k.sum()) / n
        out[n - 1:] = intercept + slope * (n - 1 - offset)
    return pd.Series(out, index=y.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length_kc"])
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    mid = ((h.rolling(n).max() + lo.rolling(n).min()) / 2 + c.rolling(n).mean()) / 2
    val = _linreg(c - mid, n, 0)
    prev = val.shift(1).fillna(0)                       # nz(val[1])
    short_sig = ((val > 0) & (val < prev)).to_numpy()
    long_sig = ((val < 0) & (val > prev)).to_numpy()

    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if short_sig[i]:
            if pos != -1:
                se[i], pos = True, -1
        elif long_sig[i] and pos != 1:
            le[i], pos = True, 1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
