"""Squeeze momentum on reversal: the squeeze momentum value (20-bar linear regression of the close's
distance from the Donchian / SMA midpoint) turning up while below -strength goes long; turning
down while above +strength goes short (always in).
Port of FMZ strategy #426259 "Squeeze Momentum on Reversal Strategy".

Source
    https://www.fmz.com/strategy/426259 (PineScript v2/v3 syntax, FMZ last modified 2023-09-09 23:57:41).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 69-112), KC length 20, strength 0.0018
    valin = linreg(close - avg(avg(highest(high, 20), lowest(low, 20)), sma(close, 20)), 20, 0)
    long  = valin < -strength and valin > nz(valin[1]);  short = valin > strength and valin < nz(valin[1])

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: strength 0.0018 is in price units (18 pips on a forex pair). It becomes
      strength_atr x ATR(14) (on BTC 0.0018 is 0 ATR). The squeeze on/off flags only colour.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426259_squeeze_momentum_turn"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "length_kc": [14, 20],
    "strength_atr": [0.0, 0.1, 0.25],
}
DEFAULT_PARAMS = {"length_kc": 20, "strength_atr": 0.0}


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
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length_kc"])
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    mid = ((h.rolling(n).max() + l.rolling(n).min()) / 2 + c.rolling(n).mean()) / 2
    valin = _linreg(c - mid, n, 0)
    prev = valin.shift(1).fillna(0.0)  # nz(valin[1])
    thr = p["strength_atr"] * _atr_pine(bars_df, ATR_LEN)
    long_ = ((valin < -thr) & (valin > prev)).to_numpy()
    short = ((valin > thr) & (valin < prev)).to_numpy()
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
