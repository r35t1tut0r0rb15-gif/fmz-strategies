"""RSI 14 crossings of 30 / 70 on the SMA 200 side, 1-minute bars: RSI up through 30 above the SMA closes a short and goes long, RSI down through 70 below the SMA closes a long and goes short; reversing.
Port of FMZ strategy #483112 "基于RSI和趋势均线的双重过滤交易策略-RSI-and-Trend-MA-Dual-Filter-Trading-Strategy" (Leading Indicator Strategy - Daily Signals).

FMZ source id: 483112

Source
    https://www.fmz.com/strategy/483112 (PineScript v5, FMZ last modified 2025-02-21 14:05:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 115-157), RSI 14 / 30 / 70; SMA 200 trend filter on; pyramiding 1; 100 % of equity, capital 100000
    crossover(rsi, 30) and close > sma200 -> close Short, entry Long;  crossunder(rsi, 70) and close < sma200 -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each signal closes the other side and enters: REVERSAL INTENDED, no other exit. The 100 % of equity
      size and the capital are sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI level crossings with an SMA trend filter.
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

NAME = "fmz_483112_rsi14_30_70_cross_sma200_side_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 7],
    "ma_length": [200, 100],
}
DEFAULT_PARAMS = {"rsi_length": 14, "ma_length": 200, "oversold": 30.0, "overbought": 70.0}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    ma = c.rolling(int(p["ma_length"])).mean()
    os_, ob = float(p["oversold"]), float(p["overbought"])
    le = (r > os_) & (r.shift(1) <= os_) & (c > ma)
    se = (r < ob) & (r.shift(1) >= ob) & (c < ma)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
