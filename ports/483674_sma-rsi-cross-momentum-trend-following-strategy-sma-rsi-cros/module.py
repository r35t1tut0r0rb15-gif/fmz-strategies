"""Close crossings of the SMA 20 with RSI 8 confirmation, hourly bars, long only: crossing up with RSI over 60 goes long, crossing down with RSI under 40 closes.
Port of FMZ strategy #483674 "交叉动能趋势跟踪策略SMA-RSI交叉动量系统-Cross-Momentum-Trend-Following-Strategy-SMA-RSI-Cross-Momentum-System" (STOCKS TO BUY).

FMZ source id: 483674

Source
    https://www.fmz.com/strategy/483674 (PineScript v5, FMZ last modified 2025-02-25 10:44:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-248), SMA 20; RSI 8; levels 60 / 40
    crossover(close, sma20) and rsi8 > 60 -> entry Buy;  crossunder(close, sma20) and rsi8 < 40 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The success / failure counters and the table are statistics only. Long only. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with RSI confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483674_close_sma20_cross_rsi8_60_40_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_length": [20, 50],
    "rsi_length": [8, 14],
}
DEFAULT_PARAMS = {"sma_length": 20, "rsi_length": 8}


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
    s = c.rolling(int(p["sma_length"])).mean()
    r = _rsi(c, int(p["rsi_length"]))
    le = (c > s) & (c.shift(1) <= s.shift(1)) & (r > 60)
    lx = (c < s) & (c.shift(1) >= s.shift(1)) & (r < 40)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
