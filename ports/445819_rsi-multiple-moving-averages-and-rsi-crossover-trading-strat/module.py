"""MACD crossings in the direction of the EMA 9 / 21 order with an RSI filter, 4-hour bars: a MACD cross up with EMA 9 above EMA 21 and the RSI 14 under 70 goes long, the mirror (RSI over 30) goes short; a
long closes when the EMAs turn bearish or the RSI goes over 70, a short when they turn bullish or the RSI goes under 30; reversing.
Port of FMZ strategy #445819 "多重均线与RSI交叉交易策略Multiple-Moving-Averages-and-RSI-Crossover-Trading-Strategy" (Candle Genie Strategy (CGS)).

FMZ source id: 445819

Source
    https://www.fmz.com/strategy/445819 (PineScript v5, FMZ last modified 2024-03-22 14:38:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 154-199), EMA 9 / 21; RSI 14, levels 70 / 30; MACD 12 / 26 / 9
    fast > slow and rsi < 70 and crossover(macd, signal) -> entry Long;  fast < slow and rsi > 30 and crossunder(macd, signal) -> entry Short
    close Long when fast < slow or rsi > 70;  close Short when fast > slow or rsi < 30

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes are called after both entries; a close after a reversing entry on the same bar leaves
      the reversal (a short entry always meets the long close's EMA test). strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "4h" from the backtest header (UTC-aligned 4-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings with EMA order and RSI filters.
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

NAME = "fmz_445819_macd_cross_ema9_21_order_rsi_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 34],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "rsi_len": 14, "ob": 70.0, "os": 30.0}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    m1, g1 = macd.shift(1), sig.shift(1)
    bull, bear = f > s, f < s
    ob, os_ = float(p["ob"]), float(p["os"])
    le = bull & (r < ob) & (macd > sig) & (m1 <= g1)
    se = bear & (r > os_) & (macd < sig) & (m1 >= g1)
    lx = (bear | (r > ob)) & ~se
    sx = (bull | (r < os_)) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
