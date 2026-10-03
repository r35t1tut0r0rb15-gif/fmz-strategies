"""Dual SMA with a confirmation count, long only. Port of FMZ strategy #103070
"简单均线策略Moving-Average-Bot-30-lines" (simple moving-average bot, 30 lines).

Source
    https://www.fmz.com/strategy/103070 (JavaScript, author "小草", FMZ last modified
    2020-10-13 14:51:55). Verbatim copy: original_source.md. Read 2026-09-29.

Original signal (original_source.md lines 55-82)
    records = GetRecords(PERIOD_M15); fast = TA.MA(records, FastPeriod); slow = TA.MA(records, SlowPeriod)
    n = _Cross(fast, slow)   # +k: fast above slow for the last k bars; -k: below for k bars
    n >= EnterPeriod and cash  -> buy;   n <= -EnterPeriod and coins -> sell all
    Defaults: FastPeriod 5, SlowPeriod 15, EnterPeriod 2.

Interpretation choices
    * _Cross is FMZ's run-length count of the sign of (fast - slow) back from the latest record;
      an equal value ends the run. The port computes the same run length on completed bars
      (current bar included); the original counts from the forming bar.
    * Signals are levels (true while the run is long enough); the engine ignores entries while
      long and exits while flat, which reproduces the cash/coins guards.
    * Long only (spot). Opposite entries cannot occur.
    * FREQ = "15min": the code requests PERIOD_M15 records explicitly. (The backtest header's
      1d period only sets FMZ's chart; the signal uses the M15 records.)
    * Sizing (99 % of balance, Slippage, 0.1 minimum, cancel-if-pending) is in
      original_sizing.txt. No costs here.
"""
import numpy as np
import pandas as pd

NAME = "fmz_103070_sma_cross_confirmed_long"
FREQ = "15min"
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [3, 5, 10],
    "slow": [15, 30, 60],
    "enter_period": [1, 2, 3],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 15, "enter_period": 2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _signed_run(diff):
    """FMZ _Cross: +k if diff > 0 for the last k bars, -k if < 0, 0 on equality or NaN."""
    d = diff.to_numpy(dtype=float)
    out = np.zeros(len(d))
    for i in range(len(d)):
        if np.isnan(d[i]) or d[i] == 0:
            out[i] = 0
        elif d[i] > 0:
            out[i] = out[i - 1] + 1 if i and out[i - 1] > 0 else 1
        else:
            out[i] = out[i - 1] - 1 if i and out[i - 1] < 0 else -1
    return pd.Series(out, index=diff.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    close = bars_df["close"]
    n = _signed_run(close.rolling(int(p["fast"])).mean() - close.rolling(int(p["slow"])).mean())
    k = int(p["enter_period"])
    long_entries = (n >= k).astype(bool)
    long_exits = (n <= -k).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_entries, long_exits, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
