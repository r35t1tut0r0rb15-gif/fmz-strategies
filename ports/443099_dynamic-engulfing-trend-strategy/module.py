"""Engulfing candles with the SuperTrend(10, 3), 1-hour bars: in an up trend a wide up bar closing over a red bar's open goes long with a stop at its low and a target beyond it, the mirror short in a down
trend; reversing.
Port of FMZ strategy #443099 "Dynamic Engulfing Trend Strategy" (Engulfing with Trend).

FMZ source id: 443099

Source
    https://www.fmz.com/strategy/443099 (PineScript v4, FMZ last modified 2024-02-29 11:24:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 164-270), SuperTrend ATR 10 x 3 on hl2 (Wilder ATR); boring 25 %, engulfing 50 %; stop level 200 "pips" (x mintick)
    bullEngulfing = uptrend and close[1] < open[1] and close > open[1] and not boring(prev body <= 25 % of range) and not (body <= 50 % of range) -> entry Buy
    exit(stop = low, limit = 2 (close + 200 mintick) - low) on the signal bar;  bear mirrored (stop = high, limit = 2 (close - 200 mintick) - high)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set on the signal bar only: the stop at its low (high), the target at twice
      close + 200 ticks less the low. Criterion 2: 200 ticks are 20 price units at mintick 0.1 on the
      BTC reading, as a fraction of the close at 42000, 4.76e-4; so sl_stop = 1 - low / close and
      tp_stop = 1 + 2 x 4.76e-4 - low / close of the signal bar (mirrored for shorts), shifted one bar
      inside stops() and re-based on the fill. A bar with no range has no body share (na), so it
      never signals. The unused exitLong tests are dropped. strategy.entry reverses: REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry from signal-bar data.
    2 generic: ADAPT, tick offset -> fraction of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_443099_supertrend_engulfing_bar_range_bracket"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "multiplier": [3.0, 2.0],
    "engulf_pct": [50, 70],
}
DEFAULT_PARAMS = {"multiplier": 3.0, "engulf_pct": 50, "periods": 10, "boring_pct": 25, "offset_frac": 4.76e-04}


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


def _trend(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = (float(p["multiplier"]) * _rma(tr, int(p["periods"]))).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    out = np.ones(m, dtype=np.int8)
    up_p = dn_p = np.nan
    d = 1
    for i in range(m):
        u, dd = hl2[i] - atr[i], hl2[i] + atr[i]
        u1 = u if np.isnan(up_p) else up_p
        d1 = dd if np.isnan(dn_p) else dn_p
        if i > 0 and cv[i - 1] > u1 and not np.isnan(u):
            u = max(u, u1)
        if i > 0 and cv[i - 1] < d1 and not np.isnan(dd):
            dd = min(dd, d1)
        if d == -1 and cv[i] > d1:
            d = 1
        elif d == 1 and cv[i] < u1:
            d = -1
        out[i] = d
        up_p, dn_p = u, dd
    return out


def _setup(bars_df, p):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    tr = _trend(bars_df, p)
    rng = (h - lo).abs().where(h != lo)
    body_pct = (o - c).abs() * 100 / rng
    boring = (body_pct.shift(1) <= float(p["boring_pct"]))
    small = (body_pct <= float(p["engulf_pct"]))
    ok = body_pct.notna() & body_pct.shift(1).notna() & ~boring & ~small
    o1, c1 = o.shift(1), c.shift(1)
    bull = (pd.Series(tr == 1, index=c.index) & (c1 < o1) & (c > o1) & ok).to_numpy()
    bear = (pd.Series(tr == -1, index=c.index) & (c1 > o1) & (c < o1) & ok).to_numpy()
    f = float(p["offset_frac"])
    l_sl = 1 - lo / c
    l_tp = 1 + 2 * f - lo / c
    s_sl = h / c - 1
    s_tp = h / c - 1 + 2 * f
    sl = pd.Series(np.where(bear, s_sl, l_sl), index=c.index)
    tp = pd.Series(np.where(bear, s_tp, l_tp), index=c.index)
    return bull, bear, sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    bull, bear, sl_s, tp_s = _setup(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and ((s_ > 0 and lv[i] <= x * (1 - s_)) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and ((s_ > 0 and hv[i] >= x * (1 + s_)) or lv[i] <= x * (1 - t_)):
                pos = 0
        if i + 1 >= m:
            continue
        if bull[i] and pos != 1:
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
        elif bear[i] and pos != -1:
            se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
