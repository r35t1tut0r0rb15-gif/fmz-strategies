"""Two-EMA turning-point stop-and-reverse with a fixed take-profit distance
("dual-MA turning point strategy, teaching example").
Port of FMZ strategy #333269 "数字货币期货双均线拐点策略教学".

Source
    https://www.fmz.com/strategy/333269 (JavaScript, author "发明者量化-小小梦", FMZ last
    modified 2025-02-18 17:34:56). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 94-157), l = number of records (r[l-1] forming)
    up   = ema1[l-2] > ema1[l-3] && ema1[l-4] > ema1[l-3]  and the same for ema2   (trough)
    down = ema1[l-2] < ema1[l-3] && ema1[l-4] < ema1[l-3]  and the same for ema2   (peak)
    up && state in (SHORT, IDLE)  -> cover short, buy  (holdPrice = r[l-1].Close)
    down && state in (LONG, IDLE) -> cover long, sell short
    LONG and r[l-1].Close - holdPrice > profitTarget -> cover;  SHORT mirror

Interpretation choices
    * up/down use completed bars only (l-2 is the last completed bar), so the signal on
      completed bar t uses EMA values at t, t-1, t-2: exactly the contract's signal bar.
      holdPrice is the price just after t closes, i.e. the fill (next open).
    * The take-profit compares the forming bar's price with holdPrice; the port checks it on each
      completed bar's close (a close condition -> exit signal, not tp_stop). Criterion 2: the
      price-unit `profitTarget` becomes `tp_atr` x Wilder ATR(14) of the entry signal bar.
    * Cover-and-open on the turning point is a one-bar reversal: REVERSAL INTENDED
      (portfolio_kwargs {}; the engine's default opposite-entry reversal applies).
    * The argument table gives no numeric defaults (its "default" column holds descriptions);
      the defaults below are declared here, the grid brackets them.
    * FREQ = "1h" from the backtest header (GetRecords() default period).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_333269_dual_ema_turning_point"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema1": [5, 10, 20],
    "ema2": [20, 40, 60],
    "tp_atr": [1.0, 2.0, 4.0],
}
DEFAULT_PARAMS = {"ema1": 10, "ema2": 40, "tp_atr": 2.0, "atr_length": 14}


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


def _atr(bars, n):
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def _turns(e):
    trough = (e > e.shift(1)) & (e.shift(2) > e.shift(1))
    peak = (e < e.shift(1)) & (e.shift(2) < e.shift(1))
    return trough, peak


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    close = bars_df["close"]
    t1, p1 = _turns(close.ewm(span=int(p["ema1"]), adjust=False).mean())
    t2, p2 = _turns(close.ewm(span=int(p["ema2"]), adjust=False).mean())
    warm = np.arange(len(close)) >= max(int(p["ema1"]), int(p["ema2"]))
    up = (t1 & t2).to_numpy() & warm
    down = (p1 & p2).to_numpy() & warm
    atr = _atr(bars_df, int(p["atr_length"])).to_numpy()
    o = bars_df["open"].to_numpy(dtype=float)
    c = close.to_numpy(dtype=float)

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pending, entry, tp, pend_tp = 0, 0, np.nan, np.nan, np.nan
    for i in range(m):
        if pending:
            pos, entry, tp, pending = pending, o[i], pend_tp, 0
        if np.isnan(atr[i]):
            continue
        if up[i] and pos != 1 and pending != 1:
            le[i], pending, pend_tp = True, 1, p["tp_atr"] * atr[i]
        elif down[i] and pos != -1 and pending != -1:
            se[i], pending, pend_tp = True, -1, p["tp_atr"] * atr[i]
        elif pos == 1 and c[i] - entry > tp:
            lx[i], pos = True, 0
        elif pos == -1 and entry - c[i] > tp:
            sx[i], pos = True, 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
