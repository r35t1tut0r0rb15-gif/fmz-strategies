"""Long-only: buy an RSI dip while the fast MA is above the slow MA, sell an RSI spike while it
is below ("cross-timeframe strategy", single timeframe in the code).
Port of FMZ strategy #345289 "跨时间周期策略".

Source
    https://www.fmz.com/strategy/345289 (JavaScript, author "一刀", FMZ last modified
    2022-02-15 09:37:09). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 63-100), fast_ma 5, slow_ma 20, rsi_period 5
    records = GetRecords(PERIOD_M15); n = _Cross(MA(fast_ma), MA(slow_ma))
    n > 0 (fast above slow) and RSI < 30 -> buy with all cash
    n < 0 (fast below slow) and RSI > 70 -> sell all coins

Interpretation choices
    * _Cross returns the signed number of bars since the last cross, so its sign is the current
      order of the two MAs. The bot polls the forming bar every 60 s; the port evaluates on
      completed bar t ([-1] -> t). TA.RSI is Wilder's.
    * Buying needs cash and selling needs coins, so the position is in from a buy condition to
      the next sell condition. Long only (spot); shorts are never emitted, so opposite entries
      cannot occur.
    * FREQ = "15min" (code requests PERIOD_M15).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_345289_ma_trend_rsi_dip_long"
FAMILY = "ma_trend_oscillator_pullback"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # code requests PERIOD_M15
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_ma": [5, 10],
    "slow_ma": [20, 40],
    "rsi_period": [5, 10],
}
DEFAULT_PARAMS = {"fast_ma": 5, "slow_ma": 20, "rsi_period": 5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    fast = c.rolling(int(p["fast_ma"])).mean()
    slow = c.rolling(int(p["slow_ma"])).mean()
    rsi = _rsi(c, int(p["rsi_period"]))
    buy = ((fast > slow) & (rsi < 30)).to_numpy()
    sell = ((fast < slow) & (rsi > 70)).to_numpy()

    m = len(c)
    entries, exits = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    in_pos = False
    for i in range(m):
        if buy[i] and not in_pos:
            entries[i], in_pos = True, True
        elif sell[i] and in_pos:
            exits[i], in_pos = True, False

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(entries, index=idx), pd.Series(exits, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
