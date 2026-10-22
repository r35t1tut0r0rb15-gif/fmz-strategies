"""Bollinger 20 / 2 re-entries with RSI 14 extremes, no bar size in the source: the close crossing back over the lower band with the RSI under 30 goes long, back under the upper band with the RSI over 70 goes short; reversing.
Port of FMZ strategy #457792 "Bollinger Bands and RSI Crossover Trading Strategy" (Bollinger Bands and RSI Strategy (band re-entries)).

FMZ source id: 457792

Source
    https://www.fmz.com/strategy/457792 (PineScript v5, FMZ last modified 2024-07-26 16:16:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 198-243), Bollinger 20 / 2; RSI 14, levels 70 / 30
    crossover(close, lower) and rsi < 30 -> entry Buy;  crossunder(close, upper) and rsi > 70 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * There is no exit: positions end at the opposite entry. The source has no backtest header and
      names no bar size: FREQ = "bar_size_pending" (rule 1); precompute builds the bars with the house
      bar_sizes.build_bars with the driver's bar_size. REVERSAL INTENDED. No sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band re-entries with RSI extremes.
    3 crypto-exchange-only: no (no exchange named).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_457792_bollinger_reentry_rsi_extreme_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 2.5],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "rsi_len": 14, "ob": 70.0, "os": 30.0}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


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
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, lo = basis + dev, basis - dev
    r = _rsi(c, int(p["rsi_len"]))
    c1 = c.shift(1)
    le = (c > lo) & (c1 <= lo.shift(1)) & (r < float(p["os"]))
    se = (c < up) & (c1 >= up.shift(1)) & (r > float(p["ob"]))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
