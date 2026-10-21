"""DEMA 10 against TEMA 8 crossings, 2-hour bars: the DEMA crossing over the TEMA goes long, crossing under goes short; reversing.
Port of FMZ strategy #437552 "DEMA与TEMA交叉策略Dual-and-Triple-Exponential-Moving-Average-Crossover-Strategy" (DEMA-TEMA Cross).

FMZ source id: 437552

Source
    https://www.fmz.com/strategy/437552 (PineScript v5, FMZ last modified 2024-01-03 16:47:08).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 138-172), DEMA 10, TEMA 8, source close
    dema = 2 ema - ema(ema);  tema = 3 (ema1 - ema2) + ema3;  crossover(dema, tema) -> entry Long;  crossunder -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.ema is seeded with the first value. REVERSAL INTENDED. No sizing code. FREQ = "2h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crossing.
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

NAME = "fmz_437552_dema_tema_cross"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dema_length": [10, 20],
    "tema_length": [8, 16],
}
DEFAULT_PARAMS = {"dema_length": 10, "tema_length": 8}


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

    def ema(x, n):
        return x.ewm(span=n, adjust=False).mean()

    nd, nt = int(p["dema_length"]), int(p["tema_length"])
    d1 = ema(c, nd)
    dema = 2 * d1 - ema(d1, nd)
    t1 = ema(c, nt)
    t2 = ema(t1, nt)
    tema = 3 * (t1 - t2) + ema(t2, nt)
    up = (dema > tema) & (dema.shift(1) <= tema.shift(1))
    dn = (dema < tema) & (dema.shift(1) >= tema.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
