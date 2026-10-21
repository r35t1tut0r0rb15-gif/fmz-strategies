"""SuperTrend (3, 1) direction with a rising or falling EMA 14, 10-minute bars: in an uptrend, a close at or above a rising EMA 14 goes long; in a downtrend, a close at or under a falling EMA 14 goes short;
reversing.
Port of FMZ strategy #439048 "Moving Average and Super Trend Tracking Stop Loss Strategy" (Santanu Strategy).

FMZ source id: 439048

Source
    https://www.fmz.com/strategy/439048 (PineScript v5, FMZ last modified 2024-01-17 11:46:01).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 151-194), SuperTrend ATR 3, factor 1; EMA 14 (EMA 44 plot only)
    direction < 0 and close >= ema 14 and rising(ema 14, 1) -> entry Buy Now;  direction > 0 and close <= ema 14 and falling(ema 14, 1) -> entry Sell Now

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are states, so the entries are sent on every qualifying bar. The EMA 44 only plots.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend direction and EMA slope.
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

NAME = "fmz_439048_supertrend_ema14_slope"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [1.0, 2.0],
    "len": [14, 30],
}
DEFAULT_PARAMS = {"factor": 1.0, "len": 14, "atr_period": 3}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _supertrend_dir(h, lo, c, factor, n):
    """Direction of Pine's ta.supertrend(factor, atrPeriod): -1 up, 1 down, nan before the ATR."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub = np.full(m, np.nan), np.full(m, np.nan)
    st, d = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        if np.isnan(atr[i]):
            continue
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            dn_dir = True
        elif st[i - 1] == ub[i - 1]:
            dn_dir = not (cv[i] > ub[i])
        else:
            dn_dir = cv[i] < lb[i]
        st[i] = ub[i] if dn_dir else lb[i]
        d[i] = 1.0 if dn_dir else -1.0
    return pd.Series(d, index=c.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    d = _supertrend_dir(h, lo, c, float(p["factor"]), int(p["atr_period"]))
    e = c.ewm(span=int(p["len"]), adjust=False).mean()
    up = (d < 0) & (c >= e) & (e > e.shift(1))
    dn = (d > 0) & (c <= e) & (e < e.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
