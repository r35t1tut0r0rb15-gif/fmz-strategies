"""Chandelier Exit direction changes, 10-minute bars, long only: the direction turning up (a close above the previous short stop line) buys, turning down (a close below the previous long stop line) closes.
Port of FMZ strategy #437792 "Chandelier Exit Strategy" (Chandelier Exit Strategy).

FMZ source id: 437792

Source
    https://www.fmz.com/strategy/437792 (PineScript v5, FMZ last modified 2024-01-05 15:57:51).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 113-158), ATR 22, multiplier 3, extremes of closes on; quantity 25 / close
    longStop = highest(close, 22) - 3 ATR, kept at max(it, longStop[1]) while close[1] > longStop[1];  shortStop = lowest(close, 22) + 3 ATR, kept at min while close[1] < shortStop[1]
    dir := close > shortStop[1] ? 1 : close < longStop[1] ? -1 : dir;  buy = dir turns 1 -> entry Buy;  sell = dir turns -1 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop lines are signal lines compared with the close at the bar close, not orders. dir starts at
      1, so the first buy needs a turn down first. Long only. The quantity 25 / close is sizing.
      FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR stop lines on closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 25 / close quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437792_chandelier_exit_long"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [3.0, 2.0],
    "length": [22, 14],
}
DEFAULT_PARAMS = {"mult": 3.0, "length": 22}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    a = (float(p["mult"]) * _atr(bars_df, n)).to_numpy()
    hc = c.rolling(n).max().to_numpy()
    lc = c.rolling(n).min().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ls, ss = np.full(m, np.nan), np.full(m, np.nan)
    d = np.ones(m)
    for i in range(m):
        raw_l, raw_s = hc[i] - a[i], lc[i] + a[i]
        lp = ls[i - 1] if i > 0 and not np.isnan(ls[i - 1]) else raw_l     # nz(longStop[1], longStop)
        sp = ss[i - 1] if i > 0 and not np.isnan(ss[i - 1]) else raw_s
        c1 = cv[i - 1] if i > 0 else np.nan
        ls[i] = max(raw_l, lp) if (c1 > lp and not np.isnan(raw_l)) else raw_l
        ss[i] = min(raw_s, sp) if (c1 < sp and not np.isnan(raw_s)) else raw_s
        prev = d[i - 1] if i > 0 else 1.0
        d[i] = 1.0 if cv[i] > sp else (-1.0 if cv[i] < lp else prev)
    dprev = np.concatenate([[np.nan], d[:-1]])
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((d == 1) & (dprev == -1), index=ix), pd.Series((d == -1) & (dprev == 1), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
