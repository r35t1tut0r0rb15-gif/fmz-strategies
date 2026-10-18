"""True strength index crosses, 3-minute bars: the TSI (5 / 12) crossing over its EMA 5 signal while the TSI is over -0.4 and the signal
still under it goes long; the mirror at +0.4 goes short (reversing).
Port of FMZ strategy #435705 "Adaptive SMI Ergodic Trading Strategy Based on Adaptive Exponential Moving Average Lines" (Adaptive SMI Ergodic Strategy).

FMZ source id: 435705

Source
    https://www.fmz.com/strategy/435705 (PineScript v5, FMZ last modified 2023-12-18 10:34:55).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 96-117), tsi(close, 5, 12), signal EMA 5, thresholds -0.4 / +0.4
    erg = tsi(close, shortlen 5, longlen 12);  sig = ema(erg, 5);  longEntry = crossover(erg, sig) and erg > -0.4 and sig < -0.4;  shortEntry = crossunder(erg, sig) and erg < 0.4 and sig > 0.4
    longEntry -> entry long;  shortEntry -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.tsi(source, short, long) is ema(ema(change, long), short) over ema(ema(|change|, long), short),
      between -1 and 1. strategy.entry reverses: REVERSAL INTENDED. FREQ = "3min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, true strength index crosses.
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

NAME = "fmz_435705_tsi_signal_cross"
FAMILY = "momentum_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "longlen": [12, 25],
    "siglen": [5, 9],
}
DEFAULT_PARAMS = {"longlen": 12, "shortlen": 5, "siglen": 5, "over_s": -0.4, "over_b": 0.4}


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
    pc = c.diff()
    ls, ss = int(p["longlen"]), int(p["shortlen"])

    def dbl(x):
        return x.ewm(span=ls, adjust=False).mean().ewm(span=ss, adjust=False).mean()

    with np.errstate(invalid="ignore", divide="ignore"):
        erg = dbl(pc) / dbl(pc.abs())
    sig = erg.ewm(span=int(p["siglen"]), adjust=False).mean()
    ob, os_ = float(p["over_b"]), float(p["over_s"])
    le = ((erg > sig) & (erg.shift(1) <= sig.shift(1)) & (erg > os_) & (sig < os_)).fillna(False).astype(bool)
    se = ((erg < sig) & (erg.shift(1) >= sig.shift(1)) & (erg < ob) & (sig > ob)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
