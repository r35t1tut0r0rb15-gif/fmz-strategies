"""Joint extreme exits, hourly bars: Williams %R 30 crossing back over -80 on the bar RSI 7 crosses back over 20 goes long; %R crossing under -20 with RSI crossing under 80 goes short; reversing.
Port of FMZ strategy #474961 "Dual Momentum Breakthrough Confirmation Quantitative Trading Strategy" (Williams %R + RSI Strategy).

FMZ source id: 474961

Source
    https://www.fmz.com/strategy/474961 (PineScript v5, FMZ last modified 2024-12-13 10:37:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-124), Williams %R 30, -20 / -80; RSI 7, 80 / 20
    crossover(wpr, -80) and crossover(rsi, 20) -> entry Buy;  crossunder(wpr, -20) and crossunder(rsi, 80) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, joint %R / RSI extreme crossings.
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

NAME = "fmz_474961_wpr30_rsi7_joint_extreme_cross_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "wpr_length": [30, 14],
    "rsi_length": [7, 14],
}
DEFAULT_PARAMS = {"wpr_length": 30, "rsi_length": 7}


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


def _xo(a, lv):
    return (a > lv) & (a.shift(1) <= lv)


def _xu(a, lv):
    return (a < lv) & (a.shift(1) >= lv)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["wpr_length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    w = (hh - c) / (hh - ll) * -100
    r = _rsi(c, int(p["rsi_length"]))
    le = _xo(w, -80) & _xo(r, 20)
    se = _xu(w, -20) & _xu(r, 80)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
