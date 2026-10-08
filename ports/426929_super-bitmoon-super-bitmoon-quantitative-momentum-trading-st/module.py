"""Super BitMoon, long only: the synthetic VIX (Williams VIX fix, 10) crossing back under its upper
2-bar band with the close above a 5-bar volatility stop goes long; RSI(10) crossing under 50
closes the long.
Port of FMZ strategy #426929 "Super BitMoon Quantitative Momentum Trading Strategy".

Source
    https://www.fmz.com/strategy/426929 (PineScript v2/v3 syntax, FMZ last modified 2023-09-15 16:13:05).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 126-171), ATR stop 5 x 1, VIX 10, band 2 x 0.01, RSI 10 / 50
    vstop: volatility stop of #426801 (max / min of closes in the trend -+ atr)
    wvf = (highest(close, 10) - low) / highest(close, 10) * 100
    upper = sma(wvf, 2) + 0.01 stdev(wvf, 2)
    crossunder(wvf, upper) and close > vstop -> entry long
    crossunder(rsi(close, 10), 50) -> entry short, which allow_entry_in(long) turns into a close

Interpretation choices (Pine rules in SURVEY_README.md)
    * Strategy direction 1 (long): shorts only close longs. Long only.
    * Same bar: from flat the entry stands; while long the close goes flat.
    * stdev is Pine's population deviation. The date range is always true.
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426929_super_bitmoon_long"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pd": [10, 22],
    "rsi_len": [10, 14],
}
DEFAULT_PARAMS = {"length": 5, "mult": 1.0, "pd": 10, "bbl": 2, "mult2": 0.01, "rsi_len": 10, "os": 50}


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


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


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


def _long_only(entry, out, index):
    """Pine order for a long-only script: an entry from flat stands (a close finds no position at
    the close); while long the entry is refused and the close goes flat."""
    target = np.zeros(len(entry), dtype=int)
    pos = 0
    for i in range(len(entry)):
        if pos == 0 and entry[i]:
            pos = 1
        elif pos == 1 and out[i]:
            pos = 0
        target[i] = pos
    return _emit(target, index)


def _vstop(bars_df, n, mult):
    atr = (mult * _atr_pine(bars_df, n)).to_numpy()
    c = bars_df["close"].to_numpy(dtype=float)
    pmax = lambda a, b: np.nan if np.isnan(a) or np.isnan(b) else max(a, b)
    pmin = lambda a, b: np.nan if np.isnan(a) or np.isnan(b) else min(a, b)
    nz = lambda x: 0.0 if np.isnan(x) else x
    out = np.full(len(c), np.nan)
    max_p = min_p = vs_p = np.nan
    up_p = None
    for i in range(len(c)):
        max1, min1 = pmax(nz(max_p), c[i]), pmin(nz(min_p), c[i])
        up_prev = True if up_p is None else up_p
        stop = max1 - atr[i] if up_prev else min1 + atr[i]
        vstop1 = pmax(nz(vs_p), stop) if up_prev else pmin(nz(vs_p), stop)
        up = bool(c[i] - vstop1 >= 0)
        changed = up != up_prev
        max_ = c[i] if changed else max1
        min_ = c[i] if changed else min1
        vs = (max_ - atr[i] if up else min_ + atr[i]) if changed else vstop1
        out[i] = vs
        max_p, min_p, vs_p, up_p = max_, min_, vs, up
    return pd.Series(out, index=bars_df.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, l = bars_df["close"], bars_df["low"]
    vstop = _vstop(bars_df, int(p["length"]), p["mult"])
    hc = c.rolling(int(p["pd"])).max()
    wvf = (hc - l) / hc * 100
    b = int(p["bbl"])
    upper = wvf.rolling(b).mean() + p["mult2"] * wvf.rolling(b).std(ddof=0)
    entry = ((wvf < upper) & (wvf.shift(1) >= upper.shift(1)) & (c > vstop)).to_numpy()
    rsi = _rsi_pine(c, int(p["rsi_len"]))
    out = ((rsi < p["os"]) & (rsi.shift(1) >= p["os"])).to_numpy()
    return _long_only(entry, out, bars_df.index)


def portfolio_kwargs(**params):
    return {}
