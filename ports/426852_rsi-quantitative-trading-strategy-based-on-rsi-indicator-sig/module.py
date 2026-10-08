"""RSI %b: the %b of a smoothed RSI within its own Bollinger band (80, 3) crossing up through 0.2
goes long, crossing down through 0.8 goes short; crossing down through 0.2 or up through 0.8
closes the position.
Port of FMZ strategy #426852 "RSI Quantitative Trading Strategy Based on RSI Indicator Signals".

Source
    https://www.fmz.com/strategy/426852 (PineScript v5, FMZ last modified 2023-09-14 20:26:49).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 148-193), RSI 14, EMA 28, BB 80 x 3, 0.2 / 0.8
    r = ema(rsi(close, 14), 28); pB = (r - lower) / (upper - lower) of bb(r, 80, 3)
    pB crosses up 0.2 -> entry long;  pB crosses down 0.8 -> entry short
    pB crosses down 0.2 or up 0.8 -> close long, close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Fills in issue order: an entry that reverses stands (the other side's close then finds
      nothing); a close of the side held goes flat. stdev is Pine's population deviation.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "3h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426852_rsi_percent_b"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "smooth": [14, 28],
    "length": [40, 80],
    "mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "smooth": 28, "length": 80, "mult": 3.0, "ovb": 0.8, "ovs": 0.2,
                  "et_short": 0.8, "et_long": 0.2}


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


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r = _rsi_pine(bars_df["close"], int(p["rsi_len"])).ewm(span=int(p["smooth"]), adjust=False).mean()
    n = int(p["length"])
    basis, sd = r.rolling(n).mean(), r.rolling(n).std(ddof=0)
    lower, upper = basis - p["mult"] * sd, basis + p["mult"] * sd
    pb = (r - lower) / (upper - lower)
    pb1 = pb.shift(1)
    buy = ((pb1 < p["et_long"]) & (pb > p["et_long"])).to_numpy()
    sell = ((pb1 > p["et_short"]) & (pb < p["et_short"])).to_numpy()
    ex = (((pb1 > p["ovs"]) & (pb < p["ovs"])) | ((pb1 < p["ovb"]) & (pb > p["ovb"]))).to_numpy()
    target = np.zeros(len(pb), dtype=int)
    pos = 0
    for i in range(len(pb)):
        before = pos
        new = -1 if sell[i] else (1 if buy[i] else before)
        if ex[i] and new == before:
            new = 0
        pos = new
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
