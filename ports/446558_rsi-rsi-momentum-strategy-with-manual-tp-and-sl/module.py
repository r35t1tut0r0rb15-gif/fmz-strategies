"""RSI 14 recoveries from 30 and falls from 70 with a 50-bar range filter, bar size from the search, with a 1 % bracket: the RSI back above 30 while its 2-bar mean is still at or under 30 (close above 70 %
of the 50-bar high) goes long, the mirror at 70 (close under 130 % of the 50-bar low) goes short; stop and target 1 % from the fill; reversing.
Port of FMZ strategy #446558 "RSI-动量策略-RSI-Momentum-Strategy-with-Manual-TP-and-SL" (RSI Strategy with Manual TP and SL).

FMZ source id: 446558

Source
    https://www.fmz.com/strategy/446558 (PineScript v5, FMZ last modified 2024-03-29 16:35:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-138), RSI 14, levels 30 / 70; 50-bar close high x 0.7 / low x 1.3; take profit 1 %, stop 1 % of the average price; trailing 20 % (unused)
    rsi > 30 and sma(rsi, 2) <= 30 and close > highest(close, 50) x 0.7 -> entry RsiLE;  rsi < 70 and sma(rsi, 2) >= 70 and close < lowest(close, 50) x 1.3 -> entry RsiSE
    exit(RsiLE, limit = avg x 1.01, stop = avg x 0.99);  exit(RsiSE, limit = avg x 0.99, stop = avg x 1.01)  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1);
      precompute builds the bars with the house bar_sizes.build_bars with the driver's bar_size. The
      bracket comes from the average price (na while flat), so it is a fixed 1 % of the fill: sl_stop
      = tp_stop = 0.01 (as #440797). The trailing-profit input is never used. strategy.entry reverses:
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed from the fill.
    2 generic: PASS, RSI threshold recoveries with a range filter, percent bracket.
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

NAME = "fmz_446558_rsi_30_70_recovery_range_filter_1pct_bracket_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [14, 7],
    "bracket": [0.01, 0.02],
}
DEFAULT_PARAMS = {"length": 14, "bracket": 0.01, "os": 30.0, "ob": 70.0}


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
    r = _rsi(c, int(p["length"]))
    r2 = r.rolling(2).mean()
    os_, ob = float(p["os"]), float(p["ob"])
    le = (r > os_) & (r2 <= os_) & (c > c.rolling(50).max() * 0.7)
    se = (r < ob) & (r2 >= ob) & (c < c.rolling(50).min() * 1.3)
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    b = float(p["bracket"])
    return {"sl_stop": b, "tp_stop": b}


def portfolio_kwargs(**params):
    return {}
