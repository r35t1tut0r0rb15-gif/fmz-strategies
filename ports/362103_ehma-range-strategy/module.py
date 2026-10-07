"""Exponential Hull MA with a band: long when the close is above the band, short when below
(the long exit and the short entry are the same condition, so it reverses).
Port of FMZ strategy #362103 "EHMA-Range-Strategy".

Source
    https://www.fmz.com/strategy/362103 (PineScript, FMZ last modified 2022-05-10 00:01:08).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 71-123), Period 180, RangeWidth 0.02, Both
    ema0(x, y) = alpha*x + (1-alpha)*nz(prev), alpha = 2/(y+1)      (zero-seeded EMA)
    EHMA = ema0(2*ema0(close, P/2) - ema0(close, P), sqrt(P))
    upper/lower = EHMA*(1 +/- 0.02)
    long: close > upper; exit long: close < lower; short: close < lower; exit short: close > upper

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the +/-2 % band becomes +/- `band_atr` x Wilder ATR(14).
    * Exit-long and short-entry fire together, so the position reverses: REVERSAL INTENDED
      (portfolio_kwargs {}). Between the bands nothing changes.
    * The zero-seeded EMAs are reproduced; the port emits nothing for the first 2*Period bars.
    * Daily bars (backtest period 1d) are broker days (17:00 New York).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362103_ehma_band_reverse"
FAMILY = "ma_envelope_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [90, 180, 270],
    "band_atr": [0.25, 0.5, 1.0],
}
DEFAULT_PARAMS = {"period": 180, "band_atr": 0.5, "atr_length": 14}


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


def _ema0(x, length):
    v = np.asarray(x, dtype=float)
    a = 2.0 / (length + 1)
    out = np.empty(len(v))
    prev = 0.0
    for i in range(len(v)):
        prev = out[i] = a * v[i] + (1 - a) * prev
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["period"])
    c = bars_df["close"].to_numpy(dtype=float)
    ehma = _ema0(2 * _ema0(c, n / 2) - _ema0(c, n), np.sqrt(n))
    band = p["band_atr"] * _atr_pine(bars_df, int(p["atr_length"])).to_numpy()
    warm = np.arange(len(c)) >= 2 * n
    return _always_in(warm & (c > ehma + band), warm & (c < ehma - band), bars_df.index)


def portfolio_kwargs(**params):
    return {}
