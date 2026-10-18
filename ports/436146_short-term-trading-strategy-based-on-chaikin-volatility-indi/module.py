"""Chaikin volatility sign, 3-hour bars: the 12-bar rate of change of the 10-bar EMA of the high-low range under zero holds a long, over zero a short (reversing); the
"Trade reverse" input flips the side.
Port of FMZ strategy #436146 "Short term Trading Strategy Based on Chaikin Volatility Indicator" (Chaikin Volatility Strategy Backtest).

FMZ source id: 436146

Source
    https://www.fmz.com/strategy/436146 (PineScript v2, FMZ last modified 2023-12-21 16:14:56).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 159-177), EMA 10 of the range, rate of change 12, trigger 0
    xROC_EMA = roc(ema(high - low, 10), 12);  pos = xROC_EMA < 0 ? 1 : xROC_EMA > 0 ? -1 : last;  possig = reverse ? -pos : pos;  entry long / short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state holds until the opposite sign; the signal is sent on the change of state only.
      strategy.entry reverses: REVERSAL INTENDED. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volatility rate of change.
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

NAME = "fmz_436146_chaikin_volatility_sign"
FAMILY = "volatility_band"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "length": [10, 14],
}
DEFAULT_PARAMS = {"reverse": False, "length": 10, "roc_length": 12, "trigger": 0.0}


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
    rng = bars_df["high"] - bars_df["low"]
    e = rng.ewm(span=int(p["length"]), adjust=False).mean()
    k = int(p["roc_length"])
    roc = (100 * (e - e.shift(k)) / e.shift(k)).to_numpy()
    trg = float(p["trigger"])
    m = len(roc)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if roc[i] < trg:
            q = 1
        elif roc[i] > trg:
            q = -1
        tgt[i] = q
    if p["reverse"]:
        tgt = -tgt
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
