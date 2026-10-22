"""Bollinger 20 / 2 extremes with RSI 14, 2-hour bars: a close under the lower band with RSI under 30 goes long, over the upper band with RSI over 70 goes short; reversing.
Port of FMZ strategy #475636 "布林带RSI均值回归增强型量化策略-Enhanced-Mean-Reversion-Strategy-with-Bollinger-Bands-and-RSI-Integration" (Mean Reversion Strategy).

FMZ source id: 475636

Source
    https://www.fmz.com/strategy/475636 (PineScript v5, FMZ last modified 2024-12-20 17:03:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-137), SMA 20, 2 sd; RSI 14, 70 / 30
    close < lower and rsi < 30 -> entry Buy;  close > upper and rsi > 70 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ =
      "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band / RSI extremes.
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

NAME = "fmz_475636_bb20_rsi30_70_extreme_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "std_dev": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "std_dev": 2.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["std_dev"]) * c.rolling(n).std(ddof=0)
    r = _rsi(c, 14)
    le = (c < basis - dev) & (r < 30)
    se = (c > basis + dev) & (r > 70)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
