"""Bars on which a MACD 12 / 26 / 9 signal crossing and an EMA 9 / 21 crossing happen together, hourly bars: both crossing up with RSI 14 over 30 goes long, both crossing down with RSI under 70 goes short; reversing.
Port of FMZ strategy #482645 "Multi Indicator Dynamic Trend Crossover Quantitative Trading Strategy" (EMA + MACD + RSI Strategy with Long and Short).

FMZ source id: 482645

Source
    https://www.fmz.com/strategy/482645 (PineScript v5, FMZ last modified 2025-02-19 15:01:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-154), EMA 9 / 21; MACD 12 / 26 / 9; RSI 14, 30 / 70
    crossover(macd, signal) and crossover(ema9, ema21) and rsi > 30 -> entry Long;  crossunder(macd, signal) and crossunder(ema9, ema21) and rsi < 70 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both crossings must fall on the same bar, as written. Entries only; each reverses the other side.
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, coincident MACD and EMA crossings with an RSI filter.
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

NAME = "fmz_482645_macd_and_ema9_21_same_bar_cross_rsi_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_ema_length": [9, 5],
    "slow_ema_length": [21, 34],
}
DEFAULT_PARAMS = {"fast_ema_length": 9, "slow_ema_length": 21, "macd_short": 12, "macd_long": 26,
                  "macd_signal": 9, "rsi_length": 14, "rsi_oversold": 30, "rsi_overbought": 70}


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

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    macd = ema(c, p["macd_short"]) - ema(c, p["macd_long"])
    sig = ema(macd, p["macd_signal"])
    f, s = ema(c, p["fast_ema_length"]), ema(c, p["slow_ema_length"])
    r = _rsi(c, int(p["rsi_length"]))
    le = xo(macd, sig) & xo(f, s) & (r > float(p["rsi_oversold"]))
    se = xo(sig, macd) & xo(s, f) & (r < float(p["rsi_overbought"]))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
