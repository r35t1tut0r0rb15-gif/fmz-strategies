"""RSI 19 crossings, 1-minute bars: the RSI crossing over 35 goes long, crossing under 70 goes short; reversing (the matching closes come after the reversing entries and leave them).
Port of FMZ strategy #444383 "基于RSI-穿越交易策略The-RSI-Crossover-Trading-Strategy" (RSI Strategy (RSI crossover)).

FMZ source id: 444383

Source
    https://www.fmz.com/strategy/444383 (PineScript v5, FMZ last modified 2024-03-11 16:05:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 109-140), RSI 19, oversold 35, overbought 70
    crossover(rsi, 35) -> entry RsiLE;  crossunder(rsi, 70) -> entry RsiSE;  crossunder(rsi, 70) -> close RsiLE;  crossover(rsi, 35) -> close RsiSE

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each close fires on the same bar as the opposite entry and is called after it, so it leaves the
      reversal (as the house call-order rule). strategy.entry reverses: REVERSAL INTENDED. No sizing
      code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI level crossings.
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

NAME = "fmz_444383_rsi19_35_70_cross_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [19, 14],
    "oversold": [35, 30],
}
DEFAULT_PARAMS = {"length": 19, "oversold": 35.0, "overbought": 70.0}


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
    r = _rsi(bars_df["close"], int(p["length"]))
    r1 = r.shift(1)
    os_, ob = float(p["oversold"]), float(p["overbought"])
    le = (r > os_) & (r1 <= os_)
    se = (r < ob) & (r1 >= ob)
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
