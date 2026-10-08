"""Triple-EMA pullback: from flat, with EMA 25 > 100 > 200, the close crossing back above EMA 25
after a pullback whose lowest close stayed between EMA 200 and EMA 25 goes long, with the stop
at the signal bar's EMA 100 distance and the target twice that (shorts mirrored); the EMA 100
distance must exceed a minimum.
Port of FMZ strategy #426487 "Triple EMA Pullback Breakout Trading Strategy".

Source
    https://www.fmz.com/strategy/426487 (PineScript v5, FMZ last modified 2023-09-12 15:12:56).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 114-207), EMA 25 / 100 / 200, R:R 2, min 50
    maxClose: set to close at crossover(close, ema1), then raised by higher closes
    minClose: set to close at crossunder(close, ema1), then lowered by lower closes
    long = flat and ema1 > ema2 > ema3 and crossover(close, ema1) and ema3 < minClose < ema1
           and close - ema2 > 50
    risk_long = (close - ema2) / close
    exit(stop = avg * (1 - risk_long), limit = avg * (1 + 2 risk_long))      (shorts mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop / target are fractions of the fill price: sl_stop = risk, tp_stop = 2 x risk from
      the signal bar, shifted one bar. Entries need a flat position, so simulate() mirrors the
      engine's stop and target from the fill bar on (upon_opposite_entry "ignore").
    * Criterion 2: the minimum distance (50 price units, "pips 00001.00") becomes min_atr x
      ATR(14) on the signal bar.
    * The date filter is hard-coded off (inTradeWindow = true). lotB / lotS size the orders only.
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426487_triple_ema_pullback"
FAMILY = "ma_trend_oscillator_pullback"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "rr": [1.5, 2.0, 3.0],
    "min_atr": [0.0, 0.5, 1.0],
}
DEFAULT_PARAMS = {"ema1": 25, "ema2": 100, "ema3": 200, "rr": 2.0, "min_atr": 0.5}


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


def _setups(bars, p):
    c = bars["close"]
    ema = lambda n: c.ewm(span=int(n), adjust=False).mean()
    e1, e2, e3 = ema(p["ema1"]), ema(p["ema2"]), ema(p["ema3"])
    d, d1 = c - e1, (c - e1).shift(1)
    xup, xdn = ((d > 0) & (d1 <= 0)).to_numpy(), ((d < 0) & (d1 >= 0)).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    mx, mn = np.full(m, np.nan), np.full(m, np.nan)
    hi = lo = np.nan
    for i in range(m):
        hi = cv[i] if xup[i] else hi
        if cv[i] > hi:
            hi = cv[i]
        lo = cv[i] if xdn[i] else lo
        if cv[i] < lo:
            lo = cv[i]
        mx[i], mn[i] = hi, lo
    mx, mn = pd.Series(mx, index=c.index), pd.Series(mn, index=c.index)
    min_dist = p["min_atr"] * _atr_pine(bars, ATR_LEN)
    long_c = ((e1 > e2) & (e2 > e3) & pd.Series(xup, index=c.index) & (mn > e3) & (mn < e1)
              & (c - e2 > min_dist))
    short_c = ((e1 < e2) & (e2 < e3) & pd.Series(xdn, index=c.index) & (mx < e3) & (mx > e1)
               & (e2 - c > min_dist))
    risk = pd.Series(np.where(long_c, (c - e2) / c, np.where(short_c, (e2 - c) / c, np.nan)), index=c.index)
    return long_c.to_numpy(), short_c.to_numpy(), risk


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_c, short_c, risk = _setups(bars_df, p)
    rk = risk.to_numpy()
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(o)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pending, frac, stop, target = 0, 0, np.nan, np.nan, np.nan
    for i in range(m):
        if pending:
            pos, e = pending, o[i]
            stop = e * (1 - pos * frac)
            target = e * (1 + pos * p["rr"] * frac)
            pending = 0
        if pos == 1 and (lo[i] <= stop or h[i] >= target):
            pos = 0
        elif pos == -1 and (h[i] >= stop or lo[i] <= target):
            pos = 0
        if pos == 0 and not pending:
            if long_c[i]:
                le[i], pending, frac = True, 1, rk[i]
            elif short_c[i]:
                se[i], pending, frac = True, -1, rk[i]
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, se, _ = simulate(bars_df, **params)
    _, _, risk = _setups(bars_df, p)
    sl = risk.where(le | se)
    return {"sl_stop": sl.shift(1), "tp_stop": (p["rr"] * sl).shift(1)}


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
