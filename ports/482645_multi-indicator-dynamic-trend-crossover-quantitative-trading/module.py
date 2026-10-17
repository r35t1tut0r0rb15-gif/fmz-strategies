"""MACD and EMA 9 / 21 crossing up on the same bar with RSI above 30 goes long, both crossing down with RSI below 70
goes short, always in, hourly bars.
Port of FMZ strategy #482645 "多指标动态趋势交叉量化交易策略-Multi-Indicator-Dynamic-Trend-Crossover-Quantitative-Trading-Strategy" (EMA + MACD + RSI Strategy with Long and Short).

FMZ source id: 482645

Source
    https://www.fmz.com/strategy/482645 (PineScript v5, FMZ last modified 2025-02-19 15:01:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-143), EMA 9 / 21, MACD 12 / 26 / 9, RSI 14 (30 / 70)
    crossover(macd, signal) and crossover(ema9, ema21) and rsi > 30 -> entry long
    crossunder(macd, signal) and crossunder(ema9, ema21) and rsi < 70 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries reverse (REVERSAL INTENDED); always in after the first signal. Signal module, no stops.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs, MACD and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
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

NAME = "fmz_482645_macd_ema_joint_cross_rsi_always_in"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 34],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "rsi_len": 14, "os": 30.0, "ob": 70.0}


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))

    def xover(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    long_e = (xover(macd, sig) & xover(f, s) & (rsi > p["os"])).astype(bool)
    short_e = (xover(sig, macd) & xover(s, f) & (rsi < p["ob"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
