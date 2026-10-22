"""Crossings of a WMA 45 and an EMA 89 of RSI 14, hourly bars: the WMA crossing over the EMA with RSI under 50 goes long, crossing under with RSI over 50 goes short; reversing.
Port of FMZ strategy #478733 "动态趋势判定RSI指标交叉策略-Dynamic-Trend-RSI-Indicator-Crossing-Strategy" (RSI + WMA + EMA Strategy).

FMZ source id: 478733

Source
    https://www.fmz.com/strategy/478733 (PineScript v5, FMZ last modified 2025-01-17 16:12:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-144), RSI 14; WMA 45 and EMA 89 of the RSI
    crossover(wma(rsi, 45), ema(rsi, 89)) and rsi < 50 -> entry Long;  crossunder and rsi > 50 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSI is written out with Pine's rma (100 when the average loss is 0, 0 when the average gain is
      0), the same as ta.rsi. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI moving-average crossings against the RSI side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG478733 (2 members, best partner #478741, Jaccard 0.829); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_478733_rsi14_wma45_ema89_cross_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "wma_length": [45, 20],
    "ema_length": [89, 50],
}
DEFAULT_PARAMS = {"wma_length": 45, "ema_length": 89, "rsi_length": 14}


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
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0).where(dn != 0, 100.0)        # down == 0 ? 100 : up == 0 ? 0 : rsi
    return rsi.where(up.notna() & dn.notna())


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    w = _wma(r, int(p["wma_length"]))
    e = r.ewm(span=int(p["ema_length"]), adjust=False).mean()
    le = (w > e) & (w.shift(1) <= e.shift(1)) & (r < 50)
    se = (w < e) & (w.shift(1) >= e.shift(1)) & (r > 50)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
