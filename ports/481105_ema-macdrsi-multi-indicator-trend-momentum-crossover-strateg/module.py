"""EMA 12 / 26 crossings on the same bar as a MACD signal crossing, hourly bars, long only: both up with RSI 14 under 70 buys, both down with RSI over 30 closes.
Port of FMZ strategy #481105 "多指标趋势动量交叉策略EMA双均线与MACDRSI协同信号系统-Multi-Indicator-Trend-Momentum-Crossover-Strategy-EMA-Dual-Moving-Average-with-MACD-RSI-Synergy-System" (EMA12 + EMA26 + MACD + RSI Strategy).

FMZ source id: 481105

Source
    https://www.fmz.com/strategy/481105 (PineScript v5, FMZ last modified 2025-02-08 15:15:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-143), EMA 12 / 26; MACD 12 / 26 / 9; RSI 14, 70 / 30; 200 % of equity
    crossover(ema12, ema26) and crossover(macd, signal) and rsi < 70 -> entry Long;  crossunder both and rsi > 30 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The MACD line is EMA 12 - EMA 26, so the EMA crossing is the MACD crossing zero; both crossings on
      one bar are rare, as written. Long only. The 200 % of equity size is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, joint EMA and MACD crossings with an RSI filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity stored, not ported.
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

NAME = "fmz_481105_ema12_26_macd_joint_cross_rsi_long"
FAMILY = "macd"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "signal_len": [9, 5],
    "rsi_high": [70, 80],
}
DEFAULT_PARAMS = {"signal_len": 9, "rsi_high": 70, "rsi_low": 30}


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
    e12 = c.ewm(span=12, adjust=False).mean()
    e26 = c.ewm(span=26, adjust=False).mean()
    macd = e12 - e26
    sig = macd.ewm(span=int(p["signal_len"]), adjust=False).mean()
    r = _rsi(c, 14)
    le = (e12 > e26) & (e12.shift(1) <= e26.shift(1)) & (macd > sig) & (macd.shift(1) <= sig.shift(1)) \
        & (r < float(p["rsi_high"]))
    lx = (e12 < e26) & (e12.shift(1) >= e26.shift(1)) & (macd < sig) & (macd.shift(1) >= sig.shift(1)) \
        & (r > float(p["rsi_low"]))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
