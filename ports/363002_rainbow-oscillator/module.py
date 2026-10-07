"""Rainbow Oscillator: a CCI / RSI / Stochastic blend (smoothed by SMA 4) crossing back above its
outer lower level goes long; crossing back below its outer upper level goes short (always in).
Port of FMZ strategy #363002 "Rainbow Oscillator".

Source
    https://www.fmz.com/strategy/363002 (PineScript v5, FMZ last modified 2022-05-13 23:11:47).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 115-215), weights 0.33 / 0.33, period 24, SMA 4 x 1,
level period 18, redundancy 0.99, RMA x 3
    magic = 0.33 cci(close, 24) + 0.33 (rsi(close, 24) - 50) + 0.34 (stoch(close, high, low, 40) - 50)
    sampled = sma(magic, 4)
    lastUpper := magic > 0 ? max(magic, magic[1]) : max(0, lastUpper[1]) * 0.99   (lastLower mirrors)
    level4up  = rma(rma(rma((magic >= 0 ? magic : lastUpper) * 2, 18), 18), 18)
    level4low = same with (magic <= 0 ? magic : lastLower)
    long  = sampled[1] < level4low[1] and sampled > level4low
    short = sampled[1] > level4up[1] and sampled < level4up
    long -> entry long; else short -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.rma re-seeds with an SMA whenever its previous value is na (Pine's own definition), so
      the early na values of lastUpper / lastLower do not stop the levels. Pine's math.max/min
      return na on an na argument; kept.
    * The "% Take profit" / "% Stop Loss" inputs are declared but never used; not ported.
    * ta.cci uses the mean absolute deviation; ta.stoch is the raw %K.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363002_rainbow_oscillator_level_return"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [14, 24, 34],
    "level_period": [12, 18],
}
DEFAULT_PARAMS = {"period": 24, "level_period": 18, "w_rsi": 0.33, "w_cci": 0.33, "stoch_len": 40,
                  "osc_ma": 4, "redundant": 0.99}


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


def _rma_pine(x, n):
    """ta.rma exactly: SMA(n) whenever the previous value is na, else Wilder recursion."""
    v = x.to_numpy(dtype=float)
    sma = x.rolling(n).mean().to_numpy()
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        prev = out[i - 1] if i else np.nan
        out[i] = sma[i] if np.isnan(prev) else (v[i] + (n - 1) * prev) / n
    return pd.Series(out, index=x.index)


def _cci(x, n):
    ma = x.rolling(n).mean()
    mad = x.rolling(n).apply(lambda a: np.abs(a - a.mean()).mean(), raw=True)
    return (x - ma) / (0.015 * mad)


def _decay(magic, r, upper):
    """lastUpper / lastLower: na-propagating as Pine's math.max / math.min."""
    m = len(magic)
    out = np.full(m, np.nan)
    for i in range(m):
        prev_m = magic[i - 1] if i else np.nan
        prev = out[i - 1] if i else np.nan
        if upper:
            out[i] = np.maximum(magic[i], prev_m) if magic[i] > 0 else np.maximum(0.0, prev) * r
        else:
            out[i] = np.minimum(magic[i], prev_m) if magic[i] <= 0 else np.minimum(0.0, prev) * r
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, k = int(p["period"]), int(p["stoch_len"])
    stoch = 100 * (c - l.rolling(k).min()) / (h.rolling(k).max() - l.rolling(k).min())
    w1, w2 = p["w_rsi"], p["w_cci"]
    magic = w2 * _cci(c, n) + w1 * (_rsi(c, n) - 50) + (1 - w2 - w1) * (stoch - 50)
    sampled = magic.rolling(int(p["osc_ma"])).mean()
    mv = magic.to_numpy()
    up_v = pd.Series(np.where(mv >= 0, mv, _decay(mv, p["redundant"], True)), index=c.index) * 2
    lo_v = pd.Series(np.where(mv <= 0, mv, _decay(mv, p["redundant"], False)), index=c.index) * 2
    lp = int(p["level_period"])
    lvl_up, lvl_lo = up_v, lo_v
    for _ in range(3):
        lvl_up, lvl_lo = _rma_pine(lvl_up, lp), _rma_pine(lvl_lo, lp)
    long_ = ((sampled.shift(1) < lvl_lo.shift(1)) & (sampled > lvl_lo)).to_numpy()
    short = ((sampled.shift(1) > lvl_up.shift(1)) & (sampled < lvl_up)).to_numpy()
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
