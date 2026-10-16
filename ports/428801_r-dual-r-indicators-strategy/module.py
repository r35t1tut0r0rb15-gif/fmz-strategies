"""RSI(6) recovery in the trend, hourly bars: above the SMA 182 with SMA 10 over SMA 20, RSI 6 crossing up
through 30 goes long; below the SMA 182 with SMA 10 under SMA 20, RSI 6 crossing down through 70 goes short.
Port of FMZ strategy #428801 "双R指标策略Dual-R-Indicators-Strategy" (Chrome).

FMZ source id: 428801

Source
    https://www.fmz.com/strategy/428801 (PineScript v3, FMZ last modified 2023-10-09 15:46:05).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 172-191), RSI 6, 30 / 70, SMA 182 / 10 / 20
    close > sma(close,182) and sma(close,10) > sma(close,20) and crossover(rsi(close,6), 30) -> entry long
    close < sma(close,182) and sma(close,10) < sma(close,20) and crossunder(rsi(close,6), 70) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The parabolic SAR is computed but never used (its plot is commented out): not ported.
    * pyramiding = 1 allows one entry per direction (no adds). strategy.entry reverses: REVERSAL
      INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and moving-average comparisons only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() pyramiding, commission and capital stored.
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

NAME = "fmz_428801_rsi6_recovery_in_trend"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [6, 14],
    "trend_length": [182, 100],
}
DEFAULT_PARAMS = {"rsi_length": 6, "trend_length": 182, "fast": 10, "slow": 20, "oversold": 30, "overbought": 70}


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
    r = _rsi(c, int(p["rsi_length"]))
    t = c.rolling(int(p["trend_length"])).mean()
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    os_, ob = p["oversold"], p["overbought"]
    long_e = ((c > t) & (f > s) & (r > os_) & (r.shift(1) <= os_)).astype(bool)
    short_e = ((c < t) & (f < s) & (r < ob) & (r.shift(1) >= ob)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
