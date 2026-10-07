"""EMA200 side + Aroon cross + Absolute Strength Histogram agreement entries from flat, with a
pivot stop and a 2R target fixed at entry.
Port of FMZ strategy #362167 "EMA-AROON-ASH".

Source
    https://www.fmz.com/strategy/362167 (PineScript v5, FMZ last modified 2022-05-10 11:29:01).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 107-237), EMA 200, Aroon 20, ASH 9/3 (RSI mode, WMA),
SL lookback 20, TP multiple 2
    long = close > EMA and crossover(AroonUp, AroonDown) and SmthBulls > SmthBears and flat
    stop = lowest(low,20) - close*0.001; target = close + (close - stop)*2   (short mirror)
    strategy.exit(limit=target, stop=stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Stop and target are fixed at entry: stops() returns sl_stop = (close - stop)/close and
      tp_stop = 2 x that, from the signal bar, shifted one bar inside stops(); vbt re-bases
      them on the fill price. Criterion 2: the 0.1 %-of-price buffer becomes `buffer_atr` x ATR(14).
    * Entries need a flat position; simulate() mirrors the engine's stop and target from the
      fill bar on to know when the position is gone (no exit signals are emitted).
    * Aroon: 100*(highestbars(high,21)+20)/20; highestbars ties take the most recent bar.
    * Only from flat: opposite entries cannot occur; portfolio_kwargs returns
      upon_opposite_entry="ignore" (rule 6). FREQ = "3min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362167_ema_aroon_ash_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [100, 200],
    "aroon_len": [14, 20, 30],
    "tp_mult": [1.5, 2.0, 3.0],
}
DEFAULT_PARAMS = {"ema_len": 200, "aroon_len": 20, "tp_mult": 2.0, "pivot_lookback": 20,
                  "ash_len": 9, "ash_smooth": 3, "buffer_atr": 0.5, "atr_length": 14}


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


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _bars_since_extreme(x, n, high):
    """ta.highestbars/lowestbars(x, n) as a non-positive offset (most recent extreme on ties)."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    for t in range(n - 1, len(v)):
        w = v[t - n + 1:t + 1][::-1]
        k = int(np.argmax(w)) if high else int(np.argmin(w))
        out[t] = -k
    return out


def _entries(bars_df, p):
    c = bars_df["close"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    n = int(p["aroon_len"])
    a_up = 100 * (_bars_since_extreme(bars_df["high"], n + 1, True) + n) / n
    a_dn = 100 * (_bars_since_extreme(bars_df["low"], n + 1, False) + n) / n
    au, ad = pd.Series(a_up, index=c.index), pd.Series(a_dn, index=c.index)
    x_up = (au > ad) & (au.shift(1) <= ad.shift(1))
    x_dn = (au < ad) & (au.shift(1) >= ad.shift(1))
    d = c.diff()
    bulls, bears = d.clip(lower=0), (-d).clip(lower=0)
    sb = _wma(_wma(bulls, int(p["ash_len"])), int(p["ash_smooth"]))
    sr = _wma(_wma(bears, int(p["ash_len"])), int(p["ash_smooth"]))
    long_c = ((c > ema) & x_up & (sb > sr)).to_numpy()
    short_c = ((c < ema) & x_dn & (sb < sr)).to_numpy()
    return long_c, short_c


def _fractions(bars_df, p):
    c = bars_df["close"]
    k = int(p["pivot_lookback"])
    buf = p["buffer_atr"] * _atr_pine(bars_df, int(p["atr_length"]))
    long_sl = (c - (bars_df["low"].rolling(k).min() - buf)) / c
    short_sl = ((bars_df["high"].rolling(k).max() + buf) - c) / c
    return long_sl, short_sl


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_c, short_c = _entries(bars_df, p)
    lsl, ssl = (s.to_numpy() for s in _fractions(bars_df, p))
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(o)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pending, frac, stop, target = 0, 0, np.nan, np.nan, np.nan
    for i in range(m):
        if pending:
            pos, e = pending, o[i]
            stop = e * (1 - pos * frac)
            target = e * (1 + pos * p["tp_mult"] * frac)
            pending = 0
        if pos == 1 and (lo[i] <= stop or h[i] >= target):
            pos = 0
        elif pos == -1 and (h[i] >= stop or lo[i] <= target):
            pos = 0
        if pos == 0 and not pending:
            if long_c[i] and lsl[i] > 0:
                le[i], pending, frac = True, 1, lsl[i]
            elif short_c[i] and ssl[i] > 0:
                se[i], pending, frac = True, -1, ssl[i]
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, se, _ = simulate(bars_df, **params)
    c = bars_df["close"]
    k = int(p["pivot_lookback"])
    buf = p["buffer_atr"] * _atr_pine(bars_df, int(p["atr_length"]))
    long_sl = (c - (bars_df["low"].rolling(k).min() - buf)) / c
    short_sl = ((bars_df["high"].rolling(k).max() + buf) - c) / c
    sl = long_sl.where(le, short_sl.where(se))
    return {"sl_stop": sl.shift(1), "tp_stop": (p["tp_mult"] * sl).shift(1)}


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
