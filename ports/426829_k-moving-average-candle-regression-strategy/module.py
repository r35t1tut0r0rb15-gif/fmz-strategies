"""MA-candle linear regression, long only: on HMA(60) candles, the 20-bar linear regression of
their close's distance from its EMA 20 turning from red to orange (falling, then rising below 0),
or turning green (rising above 0), goes long while an SMA(200)-candle SuperTrend points up; two
orange bars of the distance after a silver one close the long.
Port of FMZ strategy #426829 "K Moving Average Candle Regression Strategy".

Source
    https://www.fmz.com/strategy/426829 (PineScript v4, FMZ last modified 2023-09-14 17:50:14).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 146-285), HMA 60 candles, EMA 20, lookback 40,
0.85 / 1.01, BB 3, aggressive on, VixFix off
    oC = hma(close, 60); maDiff = oC - ema(oC, 20); val = linreg(maDiff, 20, 0)
    linRegColor = val > 0 ? (val > nz(val[1]) ? green : lime) : (val < nz(val[1]) ? red : orange)
    col = maDiff >= sma(maDiff, 20) + 3 stdev(maDiff, 20) or maDiff >= highest(maDiff, 40) 0.85
          ? lime : maDiff <= lower band or maDiff <= lowest(maDiff, 40) 1.01 ? orange : silver
    dir = SuperTrend on SMA(200) candles (ATR = sma of their range over 200, x1, no wicks)
    long = ((lrc == orange and lrc[1] == red) or (lrc == green and lrc[1] != green)) and dir > 0
    exit = col == orange and col[1] == orange and col[2] == silver and lrc != green

Interpretation choices (Pine rules in SURVEY_README.md)
    * na comparisons are false, so while val is na the colour is orange, as in Pine.
    * Same bar: from flat the entry stands; while long the entry is refused and the exit goes
      flat. stdev is Pine's population deviation.
    * Long only. FREQ = "15min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426829_ma_candle_linreg_long"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
GREEN, LIME, RED, ORANGE, SILVER = 1, 2, 3, 4, 5

GRID = {
    "loopback": [30, 60],
    "m_length": [10, 20],
    "st_length": [100, 200],
}
DEFAULT_PARAMS = {"loopback": 60, "m_length": 20, "lb": 40, "ph": 0.85, "pl": 1.01, "mult": 3.0,
                  "st_length": 200}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


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


def _hma(x, n):
    return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(round(np.sqrt(n))))


def _candle_dir(bars_df, n):
    """SuperTrend direction on SMA(n) candles, ATR = sma(range, n), no wicks."""
    oc = bars_df["close"].rolling(n).mean()
    oh = bars_df["high"].rolling(n).mean()
    ol = bars_df["low"].rolling(n).mean()
    oc1 = oc.shift(1)
    rng = pd.concat([oh, oc1], axis=1).max(axis=1, skipna=False) - pd.concat([ol, oc1], axis=1).min(axis=1, skipna=False)
    atr = rng.rolling(n).mean().to_numpy()
    ocv = oc.to_numpy()
    m = len(ocv)
    out = np.ones(m)
    ls_p = ss_p = np.nan
    d = 1
    for i in range(m):
        ls, ss = ocv[i] - atr[i], ocv[i] + atr[i]
        ls_prev = ls if np.isnan(ls_p) else ls_p
        ss_prev = ss if np.isnan(ss_p) else ss_p
        if i > 0 and ocv[i - 1] > ls_prev:
            ls = max(ls, ls_prev)
        if i > 0 and ocv[i - 1] < ss_prev:
            ss = min(ss, ss_prev)
        if d == -1 and ocv[i] > ss_prev:
            d = 1
        elif d == 1 and ocv[i] < ls_prev:
            d = -1
        out[i] = d
        ls_p, ss_p = ls, ss
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    oc = _hma(bars_df["close"], int(p["loopback"]))
    k = int(p["m_length"])
    md = oc - oc.ewm(span=k, adjust=False).mean()
    val = _linreg(md, k, 0)
    v1 = val.shift(1).fillna(0.0)  # nz(val[1])
    lrc = np.where(val > 0, np.where(val > v1, GREEN, LIME), np.where(val < v1, RED, ORANGE))
    mid, sd = md.rolling(k).mean(), md.rolling(k).std(ddof=0)
    hi_r = md.rolling(int(p["lb"])).max() * p["ph"]
    lo_r = md.rolling(int(p["lb"])).min() * p["pl"]
    col = np.where((md >= mid + p["mult"] * sd) | (md >= hi_r), LIME,
                   np.where((md <= mid - p["mult"] * sd) | (md <= lo_r), ORANGE, SILVER))
    lrc1 = np.concatenate([[0], lrc[:-1]])
    col1 = np.concatenate([[0], col[:-1]])
    col2 = np.concatenate([[0, 0], col[:-2]])
    d = _candle_dir(bars_df, int(p["st_length"]))
    entry = (((lrc == ORANGE) & (lrc1 == RED)) | ((lrc == GREEN) & (lrc1 != GREEN))) & (d > 0)
    out = (col == ORANGE) & (col1 == ORANGE) & (col2 == SILVER) & (lrc != GREEN)
    target = np.zeros(len(entry), dtype=int)
    pos = 0
    for i in range(len(entry)):
        if pos == 0 and entry[i]:
            pos = 1
        elif pos == 1 and out[i]:
            pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
