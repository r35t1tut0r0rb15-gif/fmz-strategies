"""A composite "outlook" index from a 50-bar z-score, a Gaussian-sine transform of it, the log EMA 20 / 50 ratio and a 50-bar log stability term, hourly bars: the index over 70 holds a long, under 30 a short; the stop at the bar's low / high, sent while the index is on the other side of 50, is pending; reversing.
Port of FMZ strategy #482771 "Quantum Spectral Momentum Trading Strategy with Multi Component Analysis" (Quantum Spectral Crypto Trading).

FMZ source id: 482771

Source
    https://www.fmz.com/strategy/482771 (PineScript v6, FMZ last modified 2025-02-27 17:51:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 105-198), SMA / stdev 50; EMA 20 / 50; weights 20 / 30 / 20 / 10; entries 70 / 30; exit stops at 50
    index = 50 + 20 (q - 1) + 30 log(ema20 / ema50) + 20 z + 10 sma(log(max(1e-10, |econ + q|)), 50),  q = exp(-z^2 / 2)(1 + sin(pi z / 2))
    index > 70 -> entry Long;  index < 30 -> entry Short;  index < 50 -> exit Long (stop = low);  index > 50 -> exit Short (stop = high)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are states, sent on every bar they hold (repeats are ignored). The exits are stop orders
      at the current bar's low / high, re-sent on each bar the index is on the far side of 50 and left
      working otherwise: stops() cannot express a level re-set every bar, so it is described here and kept
      pending (as #438034, mark trailing_stop_pending); positions end at the opposite entry until then.
      The standard deviation is the population one (Pine ta.stdev). REVERSAL INTENDED. No sizing code. The
      source carries the Mozilla Public License 2.0 notice. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; re-sent bar stops described (pending).
    2 generic: PASS, composite z-score / momentum index thresholds.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482771_composite_zscore_ema_ratio_index_70_30_reversal"
FAMILY = "zscore_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_length": [50, 100],
    "entry_band": [20.0, 10.0],
}
DEFAULT_PARAMS = {"sma_length": 50, "entry_band": 20.0, "ema_fast": 20, "ema_slow": 50, "w_quantum": 20.0,
                  "w_economic": 30.0, "w_statistical": 20.0, "w_lyapunov": 10.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["sma_length"])
    z = (c - c.rolling(n).mean()) / c.rolling(n).std(ddof=0)
    q = np.exp(-0.5 * z * z) * (1 + np.sin(np.pi / 2 * z))
    econ = np.log(c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
                  / c.ewm(span=int(p["ema_slow"]), adjust=False).mean())
    lyap = np.log(np.maximum(1e-10, (econ + q).abs())).rolling(n).mean()
    idx_v = (50 + float(p["w_quantum"]) * (q - 1) + float(p["w_economic"]) * econ
             + float(p["w_statistical"]) * z + float(p["w_lyapunov"]) * lyap)
    b = float(p["entry_band"])
    le = idx_v > 50 + b
    se = idx_v < 50 - b
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
