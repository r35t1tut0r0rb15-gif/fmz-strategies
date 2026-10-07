"""QQE (KivancOzbilgic): the smoothed RSI (fast line) crossing above its QQE trailing slow line goes
long; crossing below goes short (always in).
Port of FMZ strategy #365315 "Quantitative Qualitative Estimation".

Source
    https://www.fmz.com/strategy/365315 (PineScript v4, FMZ last modified 2022-05-24 11:28:43).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 75-113), RSI 14, smoothing 5
    QQEF = ema(rsi(close, 14), 5);  TR = |QQEF - QQEF[1]|
    WWMA := TR / 14 + (13/14) nz(WWMA[1]);  ATRRSI := WWMA / 14 + (13/14) nz(ATRRSI[1])
    QUP / QDN = QQEF +- 4.236 ATRRSI;  QQES recursion (line 91)
    crossover(QQEF, QQES) -> entry long; else crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The nz() seeds are kept (the Wilder averages start from 0).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365315_qqe_fast_slow_cross"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [9, 14, 21],
    "sf": [3, 5, 8],
}
DEFAULT_PARAMS = {"rsi_len": 14, "sf": 5, "factor": 4.236}


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
    n = int(p["rsi_len"])
    fast = _rsi(bars_df["close"], n).ewm(span=int(p["sf"]), adjust=False).mean().to_numpy()
    m = len(fast)
    a = 1 / n
    ww = atr = np.nan
    slow = np.full(m, np.nan)
    q_prev = np.nan
    for i in range(m):
        f1 = fast[i - 1] if i else np.nan
        tr = abs(fast[i] - f1)
        ww = a * tr + (1 - a) * (0.0 if np.isnan(ww) else ww)
        atr = a * ww + (1 - a) * (0.0 if np.isnan(atr) else atr)
        up, dn = fast[i] + atr * p["factor"], fast[i] - atr * p["factor"]
        q1 = 0.0 if np.isnan(q_prev) else q_prev
        if up < q1:
            q = up
        elif fast[i] > q1 and f1 < q1:
            q = dn
        elif dn > q1:
            q = dn
        elif fast[i] < q1 and f1 > q1:
            q = up
        else:
            q = q1
        slow[i] = q
        q_prev = q
    s1 = np.concatenate([[np.nan], slow[:-1]])
    f1a = np.concatenate([[np.nan], fast[:-1]])
    up_x = (fast > slow) & (f1a <= s1)
    dn_x = (fast < slow) & (f1a >= s1)
    return _always_in(up_x, dn_x, bars_df.index)


def portfolio_kwargs(**params):
    return {}
