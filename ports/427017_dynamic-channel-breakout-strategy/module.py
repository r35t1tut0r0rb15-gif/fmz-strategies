"""Keltner wick entry, long only: from flat, a bar whose low pokes under the lower Keltner band
(EMA 14 -+ 1.5 x EMA 14 of the true range) goes long with a 2.6 % target and a 1.3 % stop.
Port of FMZ strategy #427017 "Dynamic Channel Breakout Strategy".

Source
    https://www.fmz.com/strategy/427017 (PineScript v5, FMZ last modified 2023-09-16 22:46:42).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 179-423), Keltner 14 x 1.5 (true range), entry "Wick
out of band", static SL / TP 1.3 / 2.6 %, longs on, shorts off, delay and ATR filters off
    low < kc_lower and ATR(7) > 0 and no open position -> entry long
    exit(limit = avg * 1.026, stop = avg * 0.987)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Static stop / target are fractions of the fill price. Entries need a flat position, so
      simulate() mirrors the engine's stop and target from the fill bar on.
    * Long only (shorts off by default). The multi-timeframe Keltner only plots.
    * FREQ = "1min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427017_keltner_wick_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "kc_mult": [1.5, 2.0],
    "tp_pct": [2.6, 1.3],
    "sl_pct": [1.3, 0.65],
}
DEFAULT_PARAMS = {"kc_length": 14, "kc_mult": 1.5, "tp_pct": 2.6, "sl_pct": 1.3}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["kc_length"])
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    lower = c.ewm(span=n, adjust=False).mean() - p["kc_mult"] * tr.ewm(span=n, adjust=False).mean()
    ok = _atr_pine(bars_df, 7) > 0
    entry = ((l < lower) & ok).to_numpy()
    o, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    tp, sl = p["tp_pct"] / 100, p["sl_pct"] / 100
    m = len(o)
    le = np.zeros(m, dtype=bool)
    pos, pending, stop, target = 0, False, np.nan, np.nan
    for i in range(m):
        if pending:
            pos, pending = 1, False
            stop, target = o[i] * (1 - sl), o[i] * (1 + tp)
        if pos == 1 and (lv[i] <= stop or hv[i] >= target):
            pos = 0
        if pos == 0 and not pending and entry[i]:
            le[i], pending = True, True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
