"""RSI on five timeframes (15m, 30m, 1h, 2h, 4h) all at or above 65 goes LONG; all at or below 35
goes SHORT, as written (always in).
Port of FMZ strategy #363590 "RSI MTF Ob+Os".

Source
    https://www.fmz.com/strategy/363590 (PineScript v5, FMZ last modified 2022-05-16 18:17:17).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 58-136), chart 15m; RSI(close, 14); levels 65 / 35
    Fsec(tf, x) = request.security(tf, x, lookahead_off)[1]   (historical bars)
    rsiOb = RSI >= 65 on all five timeframes;  rsiOs = RSI <= 35 on all five
    rsiOb -> entry "Enter Long"; else rsiOs -> entry "Enter Short"

Interpretation choices (Pine rules in SURVEY_README.md)
    * lookahead_off gives the last completed bar of each timeframe, and [1] takes the value the
      previous chart bar saw: at 15-minute bar t each RSI is the one of the last block that had
      closed by the open of t. 30m / 1h / 2h / 4h blocks are built from the 15-minute bars
      (floored on UTC).
    * Overbought on every timeframe enters long (and oversold short): kept as written.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "15min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363590_rsi_mtf_extreme_momentum"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
TIMEFRAMES = (15, 30, 60, 120, 240)  # minutes

GRID = {
    "rsi_len": [9, 14, 21],
}
DEFAULT_PARAMS = {"rsi_len": 14, "overbought": 65.0, "oversold": 35.0}


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


def _block_values(bars, minutes, fn):
    """Aggregate the port's bars into `minutes` blocks (floored on UTC); fn(block_bars) -> values.
    Returns (block end times as int64 ns, values)."""
    key = bars.index.floor(f"{int(minutes)}min")
    agg = bars.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    vals = np.asarray(fn(agg), dtype=float)
    ends = (agg.index + pd.Timedelta(minutes=int(minutes))).asi8
    return ends, vals


def _asof(ends, vals, times):
    """Value of the last block that ended at or before each time (a completed block only)."""
    pos = np.searchsorted(ends, np.asarray(times.asi8), side="right") - 1
    out = np.full(len(pos), np.nan)
    ok = pos >= 0
    out[ok] = vals[pos[ok]]
    return out


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
    n = int(p["rsi_len"])
    idx = bars_df.index
    ob = np.ones(len(idx), dtype=bool)
    os_ = np.ones(len(idx), dtype=bool)
    for tf in TIMEFRAMES:
        ends, vals = _block_values(bars_df, tf, lambda b: _rsi(b["close"], n))
        v = _asof(ends, vals, idx)  # as seen at the close of the previous chart bar
        ob &= v >= p["overbought"]
        os_ &= v <= p["oversold"]
    return _always_in(ob, os_, idx)


def portfolio_kwargs(**params):
    return {}
