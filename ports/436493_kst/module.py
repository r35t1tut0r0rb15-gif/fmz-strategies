"""Know Sure Thing crossings, 1-hour bars: the KST (four smoothed rates of change, weighted 1 to 4) crossing over its 9-bar average goes long; crossing under goes short (reversing).
Port of FMZ strategy #436493 "KST策略" (KST策略).

FMZ source id: 436493

Source
    https://www.fmz.com/strategy/436493 (PineScript v4, FMZ last modified 2023-12-26 11:25:30).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 35-58), ROC 10 / 15 / 20 / 30, signal SMA 9
    KST = sma(roc(close,10),10) + 2 sma(roc(close,15),10) + 3 sma(roc(close,20),10) + 4 sma(roc(close,30),15);  signal = sma(KST, 9)
    crossover(KST, signal) -> entry long;  crossunder(KST, signal) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * roc is the percent rate of change 100 * (close / close[n] - 1). The header says @version=4 but the
      crossings are written with the ta. prefix; read as the plain crossings. REVERSAL INTENDED. The
      percent-of-equity size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rate-of-change crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_436493_kst_signal_cross"
FAMILY = "momentum_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "roc1": [10, 8],
    "sig": [9, 5],
}
DEFAULT_PARAMS = {"roc1": 10, "roc2": 15, "roc3": 20, "roc4": 30, "sig": 9}


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

    def roc(n):
        return 100.0 * (c / c.shift(int(n)) - 1.0)

    kst = (roc(p["roc1"]).rolling(10).mean() + 2 * roc(p["roc2"]).rolling(10).mean()
           + 3 * roc(p["roc3"]).rolling(10).mean() + 4 * roc(p["roc4"]).rolling(15).mean())
    sig = kst.rolling(int(p["sig"])).mean()
    up = ((kst > sig) & (kst.shift(1) <= sig.shift(1))).fillna(False).astype(bool)
    dn = ((kst < sig) & (kst.shift(1) >= sig.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
