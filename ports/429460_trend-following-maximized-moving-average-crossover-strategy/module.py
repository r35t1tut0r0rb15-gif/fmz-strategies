"""SMA 9 / SMA 50 cross with an RSI filter, long only, 2-hour bars: the fast SMA crossing above the slow one with
RSI 14 above 55 goes long, crossing below closes the long.
Port of FMZ strategy #429460 "Trend Following Maximized Moving Average Crossover Strategy" (Maximized Moving Average Crossing (by Coinrule)).

FMZ source id: 429460

Source
    https://www.fmz.com/strategy/429460 (PineScript v4, FMZ last modified 2023-10-17 13:05:29).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 150-167), SMA 9 / 50, RSI 14 > 55
    crossover(sma9, sma50) and rsi14 > 55 -> entry long; crossunder(sma9, sma50) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The date window (2020-2112) is dropped. Long only. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crosses and an RSI level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 30 % of equity, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND429460 (2 members, best partner #438470, Jaccard 0.662); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429460_sma9_50_cross_rsi_long"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "inshort": [9, 20],
    "rsi_signal": [55, 50],
}
DEFAULT_PARAMS = {"inlong": 50, "inshort": 9, "rsi_length": 14, "rsi_signal": 55}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["inshort"])).mean(), c.rolling(int(p["inlong"])).mean()
    r = _rsi(c, int(p["rsi_length"]))
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (r > p["rsi_signal"])).astype(bool)
    long_x = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
