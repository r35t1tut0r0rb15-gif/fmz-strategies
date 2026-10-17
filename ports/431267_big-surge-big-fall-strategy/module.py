"""Big-bar fades (tweakerID), 1-hour bars: a bar whose range is at least twice its 10-bar average with a body over half
the range goes long when red and short when green.
Port of FMZ strategy #431267 "Big Surge Big Fall Strategy" (Big Bar Strategy).

FMZ source id: 431267

Source
    https://www.fmz.com/strategy/431267 (PineScript v4, FMZ last modified 2023-11-06 15:48:22).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 195-237), period 10, size x 2, body 0.5, SL / TP off
    bigbar = (high - low) >= 2 x sum(high - low, 10) / 10 and |close - open| > 0.5 x (high - low)
    close < open and bigbar -> entry long;  close > open and bigbar -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The optional bar-size stop and target are off by default ("Use SL / TP" false) and not
      ported; direction both; "Reverse Trades" false.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, range and body ratios.
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

NAME = "fmz_431267_big_bar_fade"
FAMILY = "volatility_spike_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [10, 20],
    "mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"period": 10, "mult": 2.0, "body": 0.5}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    rng = h - lo
    big = (rng >= rng.rolling(int(p["period"])).mean() * p["mult"]) & ((c - o).abs() > rng * p["body"])
    lg = ((c < o) & big).astype(bool)
    sh = ((c > o) & big).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def portfolio_kwargs(**params):
    return {}
