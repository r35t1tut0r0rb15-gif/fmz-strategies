"""Millebot: from flat, the Hull MA (50) of OHLC4 turning up with the McGinley dynamic (50) rising
goes long, with a 5 % stop and a 10 % target; the Hull turning down closes it (shorts mirrored).
Port of FMZ strategy #426834 "Simple Trend Following Strategy".

Source
    https://www.fmz.com/strategy/426834 (PineScript v4, FMZ last modified 2023-09-14 18:01:07).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 135-194), McGinley 50, HMA 50 of ohlc4, SL 5 %, RRR 2
    mcg = na(mcg[1]) ? ema(close, 50) : mcg[1] + (close - mcg[1]) / (50 (close / mcg[1])^4)
    GoLong = crossover(HMA, HMA[1]) and flat and mcg / mcg[1] > 1        (confirmation off)
    GoLong and not GoLong[1] -> entry long, exit(limit = close * 1.10, stop = close * 0.95)
    isLong and crossunder(HMA, HMA[1]) -> close_all                      (shorts mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket comes from the signal close; as fractions it is applied to the fill
      (sl_stop 5 %, tp_stop 10 %).
    * Entries need a flat position, so simulate() mirrors the engine's stop and target from the
      fill bar on. The isLong / isShort flags clear only at the Hull turn, so a stopped-out
      trade's flag waits for that turn (it then closes nothing). Opposite entries cannot occur.
    * The risk-based contract count is sizing (original_sizing.txt).
    * FREQ = "4h" from the backtest header; stops on 4h bars: coarse_bar_stop.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_426834_millebot_hull_mcginley"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "hma_len": [30, 50],
    "mcg_len": [30, 50],
    "sl_pct": [3.0, 5.0],
}
DEFAULT_PARAMS = {"hma_len": 50, "mcg_len": 50, "sl_pct": 5.0, "rrr": 2.0}


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


def _mcginley(x, n):
    xv = x.to_numpy(dtype=float)
    seed = x.ewm(span=n, adjust=False).mean().to_numpy()
    out = np.full(len(xv), np.nan)
    for i in range(len(xv)):
        prev = out[i - 1] if i > 0 else np.nan
        out[i] = seed[i] if np.isnan(prev) else prev + (xv[i] - prev) / (n * (xv[i] / prev) ** 4)
    return pd.Series(out, index=x.index)


def _turns(bars_df, p):
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + l + c) / 4
    n = int(p["hma_len"])
    hma = _wma(2 * _wma(src, n // 2) - _wma(src, n), int(round(np.sqrt(n))))
    d, d1 = hma - hma.shift(1), (hma - hma.shift(1)).shift(1)
    up = ((d > 0) & (d1 <= 0)).to_numpy()
    dn = ((d < 0) & (d1 >= 0)).to_numpy()
    mcg = _mcginley(c, int(p["mcg_len"]))
    ratio = (mcg / mcg.shift(1)).to_numpy()
    return up, dn, ratio


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn, ratio = _turns(bars_df, p)
    sl, tp = p["sl_pct"] / 100, p["sl_pct"] / 100 * p["rrr"]
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(o)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pending, stop, target = 0, 0, np.nan, np.nan
    is_long = is_short = False
    for i in range(m):
        if pending:
            pos, e = pending, o[i]
            stop, target = e * (1 - pos * sl), e * (1 + pos * tp)
            pending = 0
        if pos == 1 and (lo[i] <= stop or h[i] >= target):
            pos = 0
        elif pos == -1 and (h[i] >= stop or lo[i] <= target):
            pos = 0
        flat = pos == 0 and not pending
        if up[i] and flat and ratio[i] > 1:
            le[i], pending, is_long = True, 1, True
        if is_long and dn[i]:
            if pos == 1:
                lx[i], pos = True, 0
            is_long = False
        if dn[i] and flat and ratio[i] < 1:
            se[i], pending, is_short = True, -1, True
        if is_short and up[i]:
            if pos == -1:
                sx[i], pos = True, 0
            is_short = False
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["sl_pct"] / 100 * p["rrr"]}


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
