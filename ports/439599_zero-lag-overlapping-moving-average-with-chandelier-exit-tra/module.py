"""Chandelier-exit flips on the ZLSMA 130 side, 3-minute bars: a flip of the Chandelier exit (ATR 1 x 2 on closes) to up with the close above the zero-lag LSMA goes long, a flip to down below it goes short; each
trade has a 2 % target and a 2 % stop; reversing.
Port of FMZ strategy #439599 "Zero Lag Overlapping Moving Average with Chandelier Exit Trading Strategy" (ZLSMA + Chandelier Exit).

FMZ source id: 439599

Source
    https://www.fmz.com/strategy/439599 (PineScript v5, FMZ last modified 2024-01-22 10:03:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 145-273), long TP / SL 2 % / 2 %, short TP / SL 2 % / 2 %; ZLSMA 130, offset 0, close; CE ATR 1, mult 2, closes for extremes
    zlsma = 2 linreg(close, 130) - linreg(linreg(close, 130), 130);  CE: longStop = highest(close, 1) - 2 atr(1) ratcheted, shortStop mirror, dir flips on the close crossing the previous stops
    long when close > zlsma and dir turns 1 -> entry long, exit(limit = avg x 1.02, stop = avg x 0.98);  short mirror with avg x 0.98 / 1.02
    close long when close < zlsma and dir turns -1 (and one trade open);  strategy.close("close short", ...) names no entry

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is a fixed 2 % / 2 % of the average (fill) price, sent once the position exists: the
      port starts it at the fill (sl_stop / tp_stop 0.02). The long close meets the bar of the short
      entry, which reverses (as #438020); the short close names an id that is never entered and does
      nothing. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      No sizing code. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed from the fill.
    2 generic: PASS, regression line side and Chandelier flips.
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

NAME = "fmz_439599_zlsma130_chandelier_flip_bracket"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.02, 0.01],
    "length1": [130, 50],
}
DEFAULT_PARAMS = {"tp": 0.02, "length1": 130, "sl": 0.02, "atr_len": 1, "mult": 2.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _linreg(y, n):
    """Pine's linreg(y, n, 0): the least-squares line over the last n bars, read at the newest bar."""
    k = pd.Series(np.arange(len(y), dtype=float), index=y.index)
    sy = y.rolling(n).sum()
    sky = (k * y).rolling(n).sum()
    x0 = k - (n - 1)                                   # x = k - x0 runs 0 .. n-1 inside the window
    sxy = sky - x0 * sy
    sx = n * (n - 1) / 2.0
    sxx = (n - 1) * n * (2 * n - 1) / 6.0
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    icpt = (sy - slope * sx) / n
    return icpt + slope * (n - 1)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length1"])
    l1 = _linreg(c, n)
    zl = (2 * l1 - _linreg(l1, n)).to_numpy()
    k = int(p["atr_len"])
    a = (float(p["mult"]) * _atr(bars_df, k)).to_numpy()
    hc = c.rolling(k).max().to_numpy()
    lc = c.rolling(k).min().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ls, ss = np.full(m, np.nan), np.full(m, np.nan)
    d = np.ones(m, dtype=np.int8)
    for i in range(m):
        l0, s0 = hc[i] - a[i], lc[i] + a[i]
        lp = ls[i - 1] if i > 0 and not np.isnan(ls[i - 1]) else l0
        sp = ss[i - 1] if i > 0 and not np.isnan(ss[i - 1]) else s0
        c1 = cv[i - 1] if i > 0 else np.nan
        ls[i] = max(l0, lp) if c1 > lp else l0
        ss[i] = min(s0, sp) if c1 < sp else s0
        prev = d[i - 1] if i > 0 else 1
        d[i] = 1 if cv[i] > sp else (-1 if cv[i] < lp else prev)
    dp = np.concatenate(([1], d[:-1]))
    buy = (d == 1) & (dp == -1) & (cv > zl)
    sell = (d == -1) & (dp == 1) & (cv < zl)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy, index=ix), false, pd.Series(sell, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
