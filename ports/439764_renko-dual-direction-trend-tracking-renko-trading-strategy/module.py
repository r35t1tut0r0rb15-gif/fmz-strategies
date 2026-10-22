"""Rajandran-style SuperTrend flips (factor 1, ATR 1), 1-hour bars: the trend turning up goes long, turning down goes short; reversing.
Port of FMZ strategy #439764 "双向趋势追踪-Renko-交易策略Dual-direction-Trend-Tracking-Renko-Trading-Strategy" (Stripped Down Vdub Renko Sniper Strategy).

FMZ source id: 439764

Source
    https://www.fmz.com/strategy/439764 (PineScript v4, FMZ last modified 2024-01-23 15:50:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 159-180), trend transition factor 1; period 1
    Up = hl2 - atr(1);  Dn = hl2 + atr(1);  TrendUp = close[1] > TrendUp[1] ? max(Up, TrendUp[1]) : Up;  TrendDown mirror;  Trend = close > TrendDown[1] ? 1 : close < TrendUp[1] ? -1 : previous (0)
    goLong = Trend turns 1 -> entry;  goShort = Trend turns -1 -> entry;  exit(from_entry "long" / "short", no levels)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script runs on ordinary candles (the Renko name is only the title). The two exits name entry
      ids that are never used and carry no levels: never sent. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR band flips.
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

NAME = "fmz_439764_vdub_supertrend_flip_f1_p1"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [1, 3],
    "pd": [1, 10],
}
DEFAULT_PARAMS = {"factor": 1, "pd": 1}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    a = (float(p["factor"]) * _atr(bars_df, p["pd"])).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tu, td = np.full(m, np.nan), np.full(m, np.nan)
    tr = np.zeros(m, dtype=np.int8)
    for i in range(m):
        up, dn = hl2[i] - a[i], hl2[i] + a[i]
        c1 = cv[i - 1] if i > 0 else np.nan
        tu1 = tu[i - 1] if i > 0 else np.nan
        td1 = td[i - 1] if i > 0 else np.nan
        tu[i] = max(up, tu1) if c1 > tu1 else up
        td[i] = min(dn, td1) if c1 < td1 else dn
        prev = tr[i - 1] if i > 0 else 0
        tr[i] = 1 if cv[i] > td1 else (-1 if cv[i] < tu1 else prev)
    tp = np.concatenate(([0], tr[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tr == 1) & (tp == -1), index=ix), false,
            pd.Series((tr == -1) & (tp == 1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
