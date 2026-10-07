"""RSI divergences (Libertus): against running price / RSI extremes reset at the 90-bar RSI high or
low, a bullish divergence goes long and a bearish one goes short (always in).
Port of FMZ strategy #365359 "Relative Strength Index - Divergences - Libertus".

Source
    https://www.fmz.com/strategy/365359 (PineScript v4, FMZ last modified 2022-05-24 15:25:05).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 47-111), RSI 14, lookback 90
    hb = |highestbars(rsi, 90)|;  lb = |lowestbars(rsi, 90)|
    max     := hb == 0 ? close : na(max[1]) ? close : max[1];   if close > max: max := close
    max_rsi := hb == 0 ? rsi   : na(max_rsi[1]) ? rsi : max_rsi[1]; if rsi > max_rsi: raise
    (min, min_rsi mirror with lb)
    divbear = max[1] > max[2] and rsi[1] < max_rsi and rsi <= rsi[1]
    divbull = min[1] < min[2] and rsi[1] > min_rsi and rsi >= rsi[1]
    divbull -> entry long; else divbear -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * hb == 0 is read as "the current RSI equals the highest RSI of the last 90 bars" (a tie with
      an older bar counts as the current bar); na until 90 RSI values exist.
    * Same divergence engine as #362664, with the orders the right way round here.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * No bar size in the source: FREQ = "bar_size_pending" (rule 1, 2026-10-07).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_365359_rsi_divergence_libertus"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # no bar size in the source (rule 1, 2026-10-07)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_period": [7, 14, 21],
    "lookback": [45, 90],
}
DEFAULT_PARAMS = {"rsi_period": 14, "lookback": 90}


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


def _running_extreme(at_ext, x, sign):
    """max/min with reset: x where at_ext or no history, else the previous value, then raised by x."""
    out = np.full(len(x), np.nan)
    for i in range(len(x)):
        prev = out[i - 1] if i else np.nan
        v = x[i] if (at_ext[i] or np.isnan(prev)) else prev
        if sign * x[i] > sign * v:
            v = x[i]
        out[i] = v
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    rsi_s = _rsi(c, int(p["rsi_period"]))
    k = int(p["lookback"])
    hb0 = (rsi_s >= rsi_s.rolling(k).max()).to_numpy()
    lb0 = (rsi_s <= rsi_s.rolling(k).min()).to_numpy()
    cv, rsi = c.to_numpy(dtype=float), rsi_s.to_numpy()
    mx, mxr = _running_extreme(hb0, cv, 1), _running_extreme(hb0, rsi, 1)
    mn, mnr = _running_extreme(lb0, cv, -1), _running_extreme(lb0, rsi, -1)
    lag = lambda a, j: np.concatenate([np.full(j, np.nan), a[:-j]])
    r1 = lag(rsi, 1)
    divbear = (lag(mx, 1) > lag(mx, 2)) & (r1 < mxr) & (rsi <= r1)
    divbull = (lag(mn, 1) < lag(mn, 2)) & (r1 > mnr) & (rsi >= r1)
    return _always_in(divbull, divbear, bars_df.index)


def portfolio_kwargs(**params):
    return {}
