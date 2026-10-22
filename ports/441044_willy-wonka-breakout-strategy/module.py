"""RSI 14 extremes, 3-hour bars: the RSI at or under 28 goes long, at or over 72 goes short; reversing.
Port of FMZ strategy #441044 "Willy Wonka Breakout Strategy" (Mi Estrategia).

FMZ source id: 441044

Source
    https://www.fmz.com/strategy/441044 (PineScript v5, FMZ last modified 2024-02-05 10:00:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 135-167), RSI 14; levels 72 / 28 (fixed); stop and target lines removed by the author
    rsi <= 28 -> entry Compra;  rsi >= 72 -> entry Venta

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are levels; an entry while already in that direction does nothing. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "3h" from the backtest header (bars on UTC
      multiples of 3 hours).

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

NAME = "fmz_441044_rsi_28_72_level_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 9],
    "oversold": [28, 20],
}
DEFAULT_PARAMS = {"rsi_length": 14, "oversold": 28}


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
    r = _rsi(bars_df["close"], int(p["rsi_length"]))
    os_ = float(p["oversold"])
    le = r <= os_
    se = r >= 100 - os_
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
