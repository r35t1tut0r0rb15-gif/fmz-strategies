"""Ultimate RSI (14, RMA) crossings of its EMA 14 signal on the far side of 50, 4-hour bars: crossing over the signal below 50 goes long, crossing under above 50 goes short; reversing.
Port of FMZ strategy #482453 "基于RSI信号线交叉的多周期趋势跟踪交易策略-Multi-Period-RSI-Signal-Line-Crossover-Trend-Following-Strategy" (Ultimate RSI [LuxAlgo] Strategy).

FMZ source id: 482453

Source
    https://www.fmz.com/strategy/482453 (PineScript v6, FMZ last modified 2025-02-18 15:04:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-195), length 14, RMA; signal EMA 14; 100 % of equity; capital 10000
    diff = upper > upper[1] ? range : lower < lower[1] ? -range : close - close[1];  arsi = rma(diff, 14) / rma(|diff|, 14) x 50 + 50;  signal = ema(arsi, 14)
    crossover(arsi, signal) and arsi < 50 -> close Short, entry Long;  crossunder and arsi > 50 -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * upper / lower are the 14-bar highest / lowest close and range their distance, as written; a zero
      denominator gives 50. Each signal closes the other side and enters, which is a reversal. REVERSAL
      INTENDED. The 100 % of equity size and capital are sizing. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, augmented RSI signal crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and capital stored, not ported.
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

NAME = "fmz_482453_ultimate_rsi14_signal_cross_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "smooth": [14, 7],
}
DEFAULT_PARAMS = {"length": 14, "smooth": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    up, lo = c.rolling(n).max(), c.rolling(n).min()
    r = up - lo
    d = c - c.shift(1)
    diff = d.where(~(lo < lo.shift(1)), -r).where(~(up > up.shift(1)), r)
    num, den = _rma(diff, n), _rma(diff.abs(), n)
    arsi = (num / den * 50 + 50).where(den != 0, 50.0).where(den.notna())
    sig = arsi.ewm(span=int(p["smooth"]), adjust=False).mean()
    le = (arsi > sig) & (arsi.shift(1) <= sig.shift(1)) & (arsi < 50)
    se = (arsi < sig) & (arsi.shift(1) >= sig.shift(1)) & (arsi > 50)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
