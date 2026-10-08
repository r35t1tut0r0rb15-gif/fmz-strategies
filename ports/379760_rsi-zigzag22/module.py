"""RSI zigzag (Zer3192): closes at RSI(1) crosses (up through 35 / down through 70) feed a 1 % zigzag
trend; the trend turning up goes long, turning down goes short (always in).
Port of FMZ strategy #379760 "RSI -ZIGZAG".

Source
    https://www.fmz.com/strategy/379760 (PineScript v4, author Zer3192, FMZ last modified
    2022-08-24 04:08:44). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 36-107), RSI length 1, 35 / 70, minimum change 1 %
    r1 = close at the last crossover(rsi, 35);  s1 = close at the last crossunder(rsi, 70) (0 before)
    trend > 0: r1 >= HH -> HH = r1; else s1 < HH (1 - 1 %) -> trend -1, LL = s1
    trend < 0: s1 <= LL -> LL = s1; else r1 > LL (1 + 1 %) -> trend 1, HH = s1
    crossover(trend, 0) -> entry long; else crossunder(trend, 0) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * RSI length 1 is the input default: 100 on an up close, 0 on a down close, 100 when flat
      (Pine's rsi() definition). Kept as written.
    * HH / LL start at the first bar's levels (0 before any cross), trend starts 1.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_379760_rsi_cross_zigzag"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [1, 2, 3],
    "zz_pct": [0.5, 1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 1, "zz_pct": 1.0, "over_sold": 35, "over_bought": 70}


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


def _rsi_pine(close, n):
    """rsi() as Pine defines it: 100 when the average loss is 0, 0 when the average gain is 0."""
    d = close.diff()
    up, down = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = 100.0 - 100.0 / (1.0 + up / down)
    return rsi.mask(up == 0, 0.0).mask(down == 0, 100.0).where(up.notna() & down.notna())


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
    cs = bars_df["close"]
    r = _rsi_pine(cs, int(p["length"]))
    lng = ((r > p["over_sold"]) & (r.shift(1) <= p["over_sold"])).to_numpy()
    sht = ((r < p["over_bought"]) & (r.shift(1) >= p["over_bought"])).to_numpy()
    c = cs.to_numpy(dtype=float)
    m = len(c)
    pi = p["zz_pct"] * 0.01
    trend = np.zeros(m)
    r1 = s1 = 0.0
    t, hh, ll = 1.0, np.nan, np.nan
    for i in range(m):
        if lng[i]:
            r1 = c[i]
        if sht[i]:
            s1 = c[i]
        if i == 0:
            hh, ll = r1, s1
        if t > 0:
            if r1 >= hh:
                hh = r1
            elif s1 < hh * (1 - pi):
                t, ll = -1.0, s1
        else:
            if s1 <= ll:
                ll = s1
            elif r1 > ll * (1 + pi):
                t, hh = 1.0, s1
        trend[i] = t
    prev = np.concatenate([[np.nan], trend[:-1]])
    return _always_in((trend > 0) & (prev <= 0), (trend < 0) & (prev >= 0), bars_df.index)


def portfolio_kwargs(**params):
    return {}
