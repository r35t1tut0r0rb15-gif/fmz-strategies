"""EMA 9 / 26 order with RSI 14 beyond 65 / 35, hourly bars: EMA 9 above 26 with RSI over 65 goes long, below with RSI under 35 goes short; reversing.
Port of FMZ strategy #477943 "双均线RSI趋势发散策略基于指数移动平均和相对强弱的趋势捕捉系统-Dual-EMA-RSI-Divergence-Strategy-A-Trend-Capture-System-Based-on-Exponential-Moving-Average-and-Relative-Strength" (EMA9_RSI_Strategy_LongShort).

FMZ source id: 477943

Source
    https://www.fmz.com/strategy/477943 (PineScript v5, FMZ last modified 2025-01-10 15:03:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-166), EMA 9 / 26; RSI 14, 65 / 35; "60" requests on the hourly chart
    high_1h = security("60", high) ... ;  highest(high_1h, 1) = high_1h;  divergence tests compare each value with itself;  ema9 > ema26 and rsi > 65 and not divergence -> entry Long;  ema9 < ema26 and rsi < 35 and not divergence -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "60" requests equal the hourly chart, and a 1-bar highest / lowest is the bar itself, so every
      divergence test compares a value with itself and is false. The conditions are states and repeat;
      a repeat on the held side is ignored. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA order with RSI thresholds.
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

NAME = "fmz_477943_ema9_26_order_rsi65_35_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_long": [65, 60],
    "slow": [26, 50],
}
DEFAULT_PARAMS = {"rsi_long": 65, "slow": 26, "fast": 9, "rsi_period": 14}


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
    r = _rsi(c, int(p["rsi_period"]))
    lv = float(p["rsi_long"])
    le = (f > s) & (r > lv)
    se = (f < s) & (r < 100 - lv)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
