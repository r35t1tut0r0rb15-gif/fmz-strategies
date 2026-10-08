"""Volatility stop (always in): an ATR(20) stop trailing the highest / lowest close of the current
trend; a close above it goes long, below it goes short.
Port of FMZ strategy #426801 "ATR Dynamic Profit Target and Stop Loss Strategy".

Source
    https://www.fmz.com/strategy/426801 (PineScript v2/v3 syntax, FMZ last modified 2023-09-14 16:22:53).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 126-152), length 20, mult 1
    max1 = max(nz(max_[1]), close); min1 = min(nz(min_[1]), close); up_prev = nz(up[1], true)
    stop = up_prev ? max1 - atr : min1 + atr
    vstop1 = up_prev ? max(nz(vstop[1]), stop) : min(nz(vstop[1]), stop)
    up = close - vstop1 >= 0; changed = up != up_prev
    max_ / min_ = changed ? close : max1 / min1
    vstop = changed ? (up ? max_ - atr : min_ + atr) : vstop1
    close > vstop -> entry long;  close < vstop -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written nz() starts the running min at 0 and the stop at 0; na (ATR warm-up) propagates
      through max / min as in Pine. The first valid stop therefore flips the state from the
      warm-up value.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426801_volatility_stop"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20, 30],
    "mult": [1.0, 2.0, 3.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 1.0}


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


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


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


def _pmax(a, b):
    return np.nan if np.isnan(a) or np.isnan(b) else max(a, b)


def _pmin(a, b):
    return np.nan if np.isnan(a) or np.isnan(b) else min(a, b)


def _nz(x, alt=0.0):
    return alt if (x is None or (isinstance(x, float) and np.isnan(x))) else x


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    atr = (p["mult"] * _atr_pine(bars_df, int(p["length"]))).to_numpy()
    c = bars_df["close"].to_numpy(dtype=float)
    m = len(c)
    vstop_out = np.full(m, np.nan)
    max_p = min_p = vstop_p = np.nan
    up_p = None
    for i in range(m):
        max1 = _pmax(_nz(max_p), c[i])
        min1 = _pmin(_nz(min_p), c[i])
        up_prev = True if up_p is None else up_p
        stop = max1 - atr[i] if up_prev else min1 + atr[i]
        vs_prev = _nz(vstop_p)
        vstop1 = _pmax(vs_prev, stop) if up_prev else _pmin(vs_prev, stop)
        up = bool(c[i] - vstop1 >= 0)  # na -> false
        changed = up != up_prev
        max_ = c[i] if changed else max1
        min_ = c[i] if changed else min1
        vstop = (max_ - atr[i] if up else min_ + atr[i]) if changed else vstop1
        vstop_out[i] = vstop
        max_p, min_p, vstop_p, up_p = max_, min_, vstop, up
    vs = pd.Series(vstop_out, index=bars_df.index)
    close = bars_df["close"]
    return _always_in((close > vs).to_numpy(), (close < vs).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
