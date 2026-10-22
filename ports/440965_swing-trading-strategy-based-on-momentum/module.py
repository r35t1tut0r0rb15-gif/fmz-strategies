"""SMA 20 / 50 crossings with an RSI filter, bar size pending: the SMA 20 crossing over the SMA 50 with the RSI 14 above 50 goes long, crossing under with the RSI under 50 short; reversing.
Port of FMZ strategy #440965 "Swing Trading Strategy Based on Momentum" (Swing Trading Strategy).

FMZ source id: 440965

Source
    https://www.fmz.com/strategy/440965 (PineScript v5, FMZ last modified 2024-02-04 10:59:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 131-185), SMA 20 / 50; RSI 14; MACD and Bollinger plotted only; no backtest header
    longCondition = crossover(sma20, sma50) and rsi > 50 -> entry Long;  shortCondition = crossunder(sma20, sma50) and rsi < 50 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The MACD and Bollinger values only feed plots. The source has no backtest header and names no bar
      size: FREQ = "bar_size_pending" (rule 1); precompute builds the bars with the house
      bar_sizes.build_bars(raw_1m_df, params["bar_size"]); the driver supplies bar_size (never in GRID /
      DEFAULT_PARAMS). strategy.entry reverses: REVERSAL INTENDED. No sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings and RSI.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_440965_sma20_50_cross_rsi_filter"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_ma": [20, 10],
    "long_ma": [50, 100],
}
DEFAULT_PARAMS = {"short_ma": 20, "long_ma": 50, "rsi_len": 14}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a = c.rolling(int(p["short_ma"])).mean()
    b = c.rolling(int(p["long_ma"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    up = (a > b) & (a.shift(1) <= b.shift(1)) & (r > 50)
    dn = (a < b) & (a.shift(1) >= b.shift(1)) & (r < 50)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
