"""Super Scalper (RSI filter version): a bar whose open sits more than one WMA-smoothed true range
below its close goes long when RSI(25) > RSI(100); one whose open sits that far above its close
goes short when RSI(25) < RSI(100) (always in).
Port of FMZ strategy #365373 "Super Scalper - 5 Min 15 Min".

Source
    https://www.fmz.com/strategy/365373 (PineScript v5, FMZ last modified 2022-05-24 16:20:58).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 51-107), ATR period 14 x 1 (WMA), RSI 25 / 100
    lower = close - wma(tr(true), 14);  upper = close + wma(tr(true), 14)
    open < lower -> entry long when rsi(25) > rsi(100)
    open > upper -> entry short when rsi(25) < rsi(100)

Interpretation choices (Pine rules in SURVEY_README.md)
    * stopLoss / takeProfit are computed but never passed to an order; the EMA crosses only draw.
    * Variant of #363803 with an RSI-pair filter instead of RSI > 50.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365373_super_scalper_rsi_pair"
FAMILY = "momentum_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_len": [7, 14, 28],
    "mult": [0.5, 1.0, 1.5],
}
DEFAULT_PARAMS = {"atr_len": 14, "mult": 1.0, "rsi_fast": 25, "rsi_slow": 100}


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


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


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
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    band = _wma(tr, int(p["atr_len"])) * p["mult"]
    r1, r2 = _rsi(c, int(p["rsi_fast"])), _rsi(c, int(p["rsi_slow"]))
    le = ((o < c - band) & (r1 > r2)).to_numpy()
    se = ((o > c + band) & (r1 < r2)).to_numpy()
    return _always_in(le, se, bars_df.index)


def portfolio_kwargs(**params):
    return {}
