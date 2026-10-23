"""A five-line box between VWMA-smoothed 14-bar highs (fixed when RSI 14 crosses under 70) and lows (fixed when it crosses over 30), hourly bars, long only: after the close crosses a box line, the next line up becomes the buy line and the next line down the sell line; the close crossing over the buy line goes long, crossing under the sell line closes.
Port of FMZ strategy #430551 "动态RSI矩形Grid策略RSI-Box-Grid-Strategy" (RSI Box Strategy (pseudo-Grid Bot)).

FMZ source id: 430551

Source
    https://www.fmz.com/strategy/430551 (PineScript v5, FMZ last modified 2023-10-30 11:29:30).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 329-413), RSI 14 (70 / 30); box from vwma(highest(close, 14), 14) / vwma(lowest(close, 14), 14); shorts off; strategy() commented out (pyramiding 33 there)
    gridTop = valuewhen(crossunder(rsi, 70), vwma(highest, 14));  gridBottom = valuewhen(crossover(rsi, 30), vwma(lowest, 14));  middle and two mid lines between
    a close crossing any line sets the status line to the closest line;  buy line = the line above it, sell line = the line below;  crossover(close, buy line) -> entry Long;  crossunder(close, sell line) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The status lines keep their last value (var) and the buy / sell lines change only when a status line
      equals one of the current box lines, as written (exact float equality). strategy() is commented out,
      so its pyramiding 33 does not apply: one position, entries while long ignored. Shorts are off. Long
      only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI-anchored box line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() (1 % of equity, pyramiding 33) stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the VWMA of the 14-bar highest / lowest close; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430551_rsi_anchored_vwma_box_line_cross_long"
FAMILY = "grid_lines"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 21],
    "oblvl": [70, 80],
}
DEFAULT_PARAMS = {"rsi_length": 14, "oblvl": 70}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _valuewhen0(cond, src):
    c = np.asarray(cond, dtype=bool)
    s = np.asarray(src, dtype=float)
    idx = np.maximum.accumulate(np.where(c, np.arange(len(c)), -1))
    return np.where(idx >= 0, s[np.maximum(idx, 0)], np.nan)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    n = int(p["rsi_length"])
    d = c.diff()
    r = 100 - 100 / (1 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))
    ob, os_ = float(p["oblvl"]), 100.0 - float(p["oblvl"])
    xdn = (r < ob) & (r.shift(1) >= ob)
    xup = (r > os_) & (r.shift(1) <= os_)
    vw = lambda x: (x * v).rolling(n).sum() / v.rolling(n).sum()
    hi_, lo_ = vw(c.rolling(n).max()), vw(c.rolling(n).min())
    top = _valuewhen0(xdn.to_numpy(), hi_.to_numpy())
    bot = _valuewhen0(xup.to_numpy(), lo_.to_numpy())
    mid = (top + bot) / 2
    mtop, mbot = (mid + top) / 2, (mid + bot) / 2
    lines = np.vstack([top, bot, mid, mtop, mbot])          # the source's order for the closest line
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    bull_st = bear_st = buy_l = sell_l = np.nan
    buy_p = sell_p = np.nan
    pos = 0
    for i in range(1, m):
        diffs = np.abs(cv[i] - lines[:, i])
        md = np.nanmin(diffs) if not np.all(np.isnan(diffs)) else np.nan
        closest = np.nan
        for j in range(5):
            if diffs[j] == md:
                closest = lines[j, i]
                break
        cu = np.any((cv[i] > lines[:, i]) & (cv[i - 1] <= lines[:, i - 1]))
        cd = np.any((cv[i] < lines[:, i]) & (cv[i - 1] >= lines[:, i - 1]))
        if cu:
            bull_st = closest
        if cd:
            bear_st = closest
        t, b, mi, mt, mb = lines[:, i]
        if bull_st == b:
            buy_l = mb
        if bull_st == mb:
            buy_l = mi
        if bull_st == mi:
            buy_l = mt
        if bull_st == mt:
            buy_l = t
        if bear_st == t:
            sell_l = mt
        if bear_st == mt:
            sell_l = mi
        if bear_st == mi:
            sell_l = mb
        if bear_st == mb:
            sell_l = b
        l_sig = cv[i] > buy_l and cv[i - 1] <= buy_p
        s_sig = cv[i] < sell_l and cv[i - 1] >= sell_p
        if pos == 1 and s_sig:                          # a repeat entry leaves the long unchanged, the close acts
            lx[i], pos = True, 0
        elif pos == 0 and l_sig and i + 1 < m:          # from flat the close has nothing to close
            le[i], pos = True, 1
        buy_p, sell_p = buy_l, sell_l
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
