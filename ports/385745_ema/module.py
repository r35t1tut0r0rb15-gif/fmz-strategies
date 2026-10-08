"""Range filter + EMA 50 / 200 (from flat): a new range-filter buy signal on a green bar above
EMA 50 with EMA 50 above EMA 200 goes long; the mirror goes short. Each position has a fixed stop
and a tick-based trailing stop.
Port of FMZ strategy #385745 "来自油管大神的双EMA均线策略" (Range Filter - B&S Signals + EMA).

Source
    https://www.fmz.com/strategy/385745 (PineScript v4/v5 mix, author 发明者量化-小小梦, FMZ last
    modified 2022-10-10 08:57:09). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 57-169), swing period 20 x 3.5, EMA 50 / 200,
loss 30 ticks, trail points 30 / offset 30 ticks
    filt: range filter (array form): moves to src - r / src + r when src leaves +- r around it
    fdir = filt rising / falling; longCond = src > filt and src != src[1] and fdir == 1 (short mirrors)
    longCondition = longCond and CondIni[1] == -1
    buy = longCondition and ema50 > ema200 and close > open and close > ema50 and flat -> entry long,
    exit(loss = 30, trail_points = 30, trail_offset = 30)   (shorts mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 30-tick loss is instrument-specific. It becomes loss_atr x ATR(14) at the
      signal bar, an sl_stop fraction shifted one bar inside stops().
    * The tick-based trailing stop is rule 2: mark trailing_stop_pending, not emitted.
    * Entries need a flat position: simulate() mirrors the engine's stop from the fill bar on;
      opposite entries cannot occur (portfolio_kwargs upon_opposite_entry="ignore", rule 6).
    * FREQ = "15min" from the backtest header (ETH pair in the header only).

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_385745_range_filter_ema_trend_flat"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "rng_per": [20, 40],
    "rng_qty": [2.5, 3.5],
    "loss_atr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"rng_per": 20, "rng_qty": 3.5, "fast": 50, "slow": 200, "loss_atr": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _smoothrng(x, t, m):
    avrng = (x - x.shift(1)).abs().ewm(span=t, adjust=False).mean()
    return avrng.ewm(span=t * 2 - 1, adjust=False).mean() * m


def _rngfilt(x, r):
    """Range filter: follows x only when it moves more than r away; nz(prev) = 0 at the start."""
    xv, rv = x.to_numpy(dtype=float), r.to_numpy(dtype=float)
    out = np.full(len(xv), np.nan)
    for i in range(len(xv)):
        prev = out[i - 1] if i and not np.isnan(out[i - 1]) else 0.0
        if xv[i] > prev:
            out[i] = prev if xv[i] - rv[i] < prev else xv[i] - rv[i]
        else:
            out[i] = prev if xv[i] + rv[i] > prev else xv[i] + rv[i]
    return pd.Series(out, index=x.index)


def _up_down_counts(f):
    fv = f.to_numpy(dtype=float)
    up, dn = np.zeros(len(fv)), np.zeros(len(fv))
    for i in range(1, len(fv)):
        if fv[i] > fv[i - 1]:
            up[i], dn[i] = up[i - 1] + 1, 0
        elif fv[i] < fv[i - 1]:
            up[i], dn[i] = 0, dn[i - 1] + 1
        else:
            up[i], dn[i] = up[i - 1], dn[i - 1]
    return up, dn


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


def _conditions(bars_df, p):
    cs = bars_df["close"]
    r = _smoothrng(cs, int(p["rng_per"]), float(p["rng_qty"])).to_numpy()
    x = cs.to_numpy(dtype=float)
    m = len(x)
    filt = np.full(m, np.nan)
    f = x[0] if m else np.nan
    for i in range(m):
        prev = f
        if x[i] - r[i] > prev:
            f = x[i] - r[i]
        if x[i] + r[i] < prev:
            f = x[i] + r[i]
        filt[i] = f
    fdir = np.zeros(m)
    for i in range(1, m):
        fdir[i] = 1.0 if filt[i] > filt[i - 1] else (-1.0 if filt[i] < filt[i - 1] else fdir[i - 1])
    x1 = np.concatenate([[np.nan], x[:-1]])
    moved = (x > x1) | (x < x1)
    lc = (x > filt) & moved & (fdir == 1)
    sc = (x < filt) & moved & (fdir == -1)
    ini = np.zeros(m)
    for i in range(m):
        ini[i] = 1.0 if lc[i] else (-1.0 if sc[i] else (ini[i - 1] if i else 0.0))
    ini1 = np.concatenate([[0.0], ini[:-1]])
    o = bars_df["open"].to_numpy(dtype=float)
    ef = cs.ewm(span=int(p["fast"]), adjust=False).mean().to_numpy()
    es = cs.ewm(span=int(p["slow"]), adjust=False).mean().to_numpy()
    buy = lc & (ini1 == -1) & (ef > es) & (x > o) & (x > ef)
    sell = sc & (ini1 == 1) & (ef < es) & (x < o) & (x < ef)
    frac = (p["loss_atr"] * _atr_pine(bars_df, ATR_LEN) / cs).to_numpy()
    return buy, sell, frac


def _entries(bars_df, p):
    buy, sell, frac = _conditions(bars_df, p)
    o, h, l = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(o)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pending, f, stop = 0, 0, np.nan, np.nan
    for i in range(m):
        if pending:
            pos, pending = pending, 0
            stop = o[i] * (1 - pos * f)
        if pos == 1 and l[i] <= stop:
            pos = 0
        elif pos == -1 and h[i] >= stop:
            pos = 0
        if pos == 0 and not pending and frac[i] > 0:
            if buy[i]:
                le[i], pending, f = True, 1, frac[i]
            elif sell[i]:
                se[i], pending, f = True, -1, frac[i]
    return le, se, frac


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _entries(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, frac = _entries(bars_df, p)
    sl = pd.Series(frac, index=bars_df.index).where(pd.Series(le | se, index=bars_df.index))
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
