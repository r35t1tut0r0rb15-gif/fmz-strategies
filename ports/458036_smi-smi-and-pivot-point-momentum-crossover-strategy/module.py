"""A stochastic-momentum-style oscillator (the close against its 8-bar close range midpoint, SMA 6) crossing its SMA 6 signal, 1-hour bars: the cross up goes long, the cross down goes short; reversing.
Port of FMZ strategy #458036 "SMI与枢轴点结合的动量交叉策略-SMI-and-Pivot-Point-Momentum-Crossover-Strategy" (SMI Strategy).

FMZ source id: 458036

Source
    https://www.fmz.com/strategy/458036 (PineScript v5, FMZ last modified 2024-07-29 14:03:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 196-230), range 8 of the close; SMI = sma((close - mid) / (h - l) x 100, 6); signal sma 6
    crossover(smi, signal) -> entry Buy;  crossunder(smi, signal) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The range uses the close's own highest / lowest, as written (not high / low); a flat range gives
      na. There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, momentum-oscillator signal crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458036_close_range_smi_signal_cross_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "smi_len": [8, 14],
    "smi_k": [6, 3],
    "smi_d": [6, 3],
}
DEFAULT_PARAMS = {"smi_len": 8, "smi_k": 6, "smi_d": 6}


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
    n = int(p["smi_len"])
    hh, ll = c.rolling(n).max(), c.rolling(n).min()
    rng = hh - ll
    d = (c - (hh + ll) / 2) / rng.where(rng != 0) * 100
    smi = d.rolling(int(p["smi_k"])).mean()
    sig = smi.rolling(int(p["smi_d"])).mean()
    le = (smi > sig) & (smi.shift(1) <= sig.shift(1))
    se = (smi < sig) & (smi.shift(1) >= sig.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
