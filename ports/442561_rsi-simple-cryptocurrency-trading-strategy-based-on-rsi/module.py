"""RSI 14 levels, 1-minute bars: the RSI under 30 goes long, over 70 goes short (re-sent each bar the level holds); the close conditions can never fire; reversing.
Port of FMZ strategy #442561 "基于RSI的简单密码货币交易策略Simple-Cryptocurrency-Trading-Strategy-Based-on-RSI" (Larry Williams Simple Crypto Strategy).

FMZ source id: 442561

Source
    https://www.fmz.com/strategy/442561 (PineScript v4, FMZ last modified 2024-02-22 17:44:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 122-152), RSI 14; overbought 70, oversold 30
    rsi < 30 -> entry Buy;  rsi > 70 -> entry Sell;  (rsi < 30 and rsi > 30) -> close Buy;  (rsi > 70 and rsi < 70) -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each close condition needs the RSI on both sides of one level at once, so neither ever fires; the
      position changes only by reversal. Same-side repeats are refused (default pyramiding).
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels.
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

NAME = "fmz_442561_rsi14_level_reversal_1m"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "oversold": [30, 20],
}
DEFAULT_PARAMS = {"length": 14, "oversold": 30}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["length"]))
    lo_ = float(p["oversold"])
    le = r < lo_
    se = r > 100.0 - lo_
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
