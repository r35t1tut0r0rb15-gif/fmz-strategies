"""Combo: the 2/20 EMA position and an Ehlers bandpass-filter zone position must agree; both long
goes long, both short goes short, any disagreement closes the position.
Port of FMZ strategy #362638 "Combo 2/20 EMA & Bandpass Filter".

Source
    https://www.fmz.com/strategy/362638 (PineScript v5, FMZ last modified 2022-05-12 16:09:47).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 68-118), Length 14, LengthBPF 20, Delta 0.5, zones +-5
    EMA20: xXA = ema(close, 14); nHH = max(high, high[1]); nLL = min(low, low[1])
           nXS = (nLL > xXA or nHH < xXA) ? nLL : nHH
           pos = nXS > close[1] ? -1 : nXS < close[1] ? 1 : pos[1]
    BPF:   beta = cos(3.14 * (360 / L) / 180); gamma = 1 / cos(3.14 * (720 * Delta / L) / 180)
           alpha = gamma - sqrt(gamma^2 - 1)
           BP = 0.5 (1 - alpha)(hl2 - hl2[2]) + beta (1 + alpha) nz(BP[1]) - alpha nz(BP[2])
           pos = BP > SellZone ? 1 : BP <= BuyZone ? -1 : pos[1]
    both 1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: SellZone 5 / BuyZone -5 are price units. They become +-zone_atr x ATR(14)
      (Pine ta.atr) on the same bar.
    * The start-date filter (from 2005-01-01) is a backtest window and is dropped. "Trade
      reverse" defaults to false and is not ported.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}). close_all -> both exits.
    * No bar size in the source: FREQ = "bar_size_pending" (rule 1, 2026-10-07).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_362638_combo_ema20_bandpass"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # no bar size in the source (rule 1, 2026-10-07)
PERIODS_PER_YEAR_OVERRIDE = None
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "length": [10, 14, 20],
    "zone_atr": [0.1, 0.5, 1.0],
}
DEFAULT_PARAMS = {"length": 14, "length_bpf": 20, "delta": 0.5, "zone_atr": 0.5}


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


def _pos_ema20(bars, n):
    h, l, c = bars["high"], bars["low"], bars["close"]
    xa = c.ewm(span=n, adjust=False).mean()
    hh = np.maximum(h, h.shift(1))
    ll = np.minimum(l, l.shift(1))
    xs = np.where((ll > xa) | (hh < xa), ll, hh)
    pc = c.shift(1).to_numpy()
    out = np.zeros(len(c))
    for i in range(len(c)):
        prev = out[i - 1] if i else 0.0
        out[i] = -1.0 if xs[i] > pc[i] else (1.0 if xs[i] < pc[i] else prev)
    return out


def _pos_bpf(bars, n, delta, zone):
    x = ((bars["high"] + bars["low"]) / 2).to_numpy()
    beta = np.cos(3.14 * (360 / n) / 180)
    gamma = 1 / np.cos(3.14 * (720 * delta / n) / 180)
    alpha = gamma - np.sqrt(gamma * gamma - 1)
    m = len(x)
    bp = np.full(m, np.nan)
    out = np.zeros(m)
    for i in range(m):
        if i >= 2:
            b1 = 0.0 if np.isnan(bp[i - 1]) else bp[i - 1]
            b2 = 0.0 if np.isnan(bp[i - 2]) else bp[i - 2]
            bp[i] = 0.5 * (1 - alpha) * (x[i] - x[i - 2]) + beta * (1 + alpha) * b1 - alpha * b2
        prev = out[i - 1] if i else 0.0
        out[i] = 1.0 if bp[i] > zone[i] else (-1.0 if bp[i] <= -zone[i] else prev)
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    zone = (float(p["zone_atr"]) * _atr_pine(bars_df, ATR_LEN)).to_numpy()
    a = _pos_ema20(bars_df, int(p["length"]))
    b = _pos_bpf(bars_df, int(p["length_bpf"]), float(p["delta"]), zone)
    pos = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0))
    idx = bars_df.index
    flat = pd.Series(pos == 0, index=idx)
    return pd.Series(pos == 1, index=idx), flat, pd.Series(pos == -1, index=idx), flat.copy()


def portfolio_kwargs(**params):
    return {}
