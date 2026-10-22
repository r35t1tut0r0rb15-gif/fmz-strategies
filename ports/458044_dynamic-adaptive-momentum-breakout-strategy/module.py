"""Engulfing bars with a rising adaptive momentum, 1-hour bars: a bullish engulfing bar (body filters) with the EMA 7 of an adaptive-length momentum rising goes long, the bearish mirror with it falling goes short; each side is closed 4 bars after its fill; reversing.
Port of FMZ strategy #458044 "Dynamic Adaptive Momentum Breakout Strategy" (Adaptive Momentum Strategy).

FMZ source id: 458044

Source
    https://www.fmz.com/strategy/458044 (PineScript v5, FMZ last modified 2024-07-29 14:36:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 246-369), momentum length adapts 10-40 by 2 % a bar (ATR 7 vs ATR 14); EMA 7 smoothing; body filters 0.5 / 0.5; hold 3 bars after the fill bar
    dynamicLen = max(10, len x 0.98) if atr7 > atr14 else min(40, len x 1.02);  value = ema(mom(close, int(len)), 7);  slope = value - value[1]
    bullish engulfing (body >= 0.5 x previous, previous >= 0.5 x mean of 5) and slope > 0 and no long timer -> entry Long, timer = bar + 1
    the mirror -> entry Short;  bar - timer >= 3 -> close that side, clear its timer

Interpretation choices (Pine rules in SURVEY_README.md)
    * The momentum length is a var that shrinks 2 % a bar while the ATR 7 is over the ATR 14 and grows
      2 % otherwise, within 10-40, and is truncated to an integer, as written. Each side has its own
      timer, set on its entry call and cleared at its close, so a new entry on a side waits for that
      side's timer; an opposite entry reverses (the reversed side's later close finds nothing to
      close). REVERSAL INTENDED. The margin settings are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the time exits are bar counts.
    2 generic: PASS, engulfing bars with adaptive momentum.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the margin settings stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458044_engulfing_adaptive_momentum_timed_exit_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hold": [3, 6],
    "ema_len": [7, 14],
}
DEFAULT_PARAMS = {"hold": 3, "ema_len": 7, "min_len": 10, "max_len": 40, "pct": 0.02,
                  "body_cur": 0.5, "body_prev": 0.5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    hv = (_atr(bars_df, 7) > _atr(bars_df, 14)).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lo_l, hi_l, k = float(p["min_len"]), float(p["max_len"]), float(p["pct"])
    dyn = (lo_l + hi_l) / 2.0
    mom = np.full(m, np.nan)
    for i in range(m):
        dyn = max(lo_l, dyn * (1 - k)) if hv[i] else min(hi_l, dyn * (1 + k))
        n = int(dyn)
        if i - n >= 0:
            mom[i] = cv[i] - cv[i - n]
    value = pd.Series(mom, index=c.index).ewm(span=int(p["ema_len"]), adjust=False).mean()
    slope = value - value.shift(1)
    body, pbody = (c - o).abs(), (c.shift(1) - o.shift(1)).abs()
    avg5 = sum((c.shift(j) - o.shift(j)).abs() for j in range(1, 6)) / 5
    size_ok = (body >= float(p["body_cur"]) * pbody) & (pbody >= float(p["body_prev"]) * avg5)
    o1, c1 = o.shift(1), c.shift(1)
    bull = (c >= o) & (c1 <= o1) & (o <= c1) & (c >= o1) & size_ok & (slope > 0)
    bear = (c <= o) & (c1 >= o1) & (o >= c1) & (c <= o1) & size_ok & (slope < 0)
    bv, sv = bull.to_numpy(), bear.to_numpy()
    hold = int(p["hold"])
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, lt, st = 0, None, None
    for i in range(m):
        cur = pos
        if bv[i] and lt is None:
            if cur != 1:
                cur = 1
            lt = i + 1
        if sv[i] and st is None:
            if cur != -1:
                cur = -1
            st = i + 1
        if lt is not None and i - lt >= hold:
            if pos == 1 and cur == 1:
                cur = 0
            lt = None
        if st is not None and i - st >= hold:
            if pos == -1 and cur == -1:
                cur = 0
            st = None
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
