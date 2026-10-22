"""CCI and MACD sign states, 1-hour bars: a CCI 14 over 100 with the MACD (12, 26) above zero, or a CCI over -100 with the MACD below zero, holds a long; the mirrored tests hold a short; reversing; the entry is
sent on every bar of the state.
Port of FMZ strategy #439605 "RSI指标结合CCI指标的量化交易策略RSI-amp-CCI-Combination-Quantitative-Trading-Strategy" (MACD+CCI Strategy).

FMZ source id: 439605

Source
    https://www.fmz.com/strategy/439605 (PineScript v3, FMZ last modified 2024-01-22 10:33:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 174-207), CCI 14 of close; MACD 12 / 26, signal 2 (unused)
    longCond = cci > 100 and macd > 0 or cci > -100 and macd < 0;  shortCond = cci < -100 and macd < 0 or cci < 100 and macd > 0;  entry long / entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's precedence: (cci > 100 and macd > 0) or (cci > -100 and macd < 0), and the same for the
      short test; the two cannot hold together, and a MACD of exactly zero holds neither. A same-side
      entry while in the position is ignored. strategy.entry reverses: REVERSAL INTENDED. No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, CCI levels and the MACD sign.
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

NAME = "fmz_439605_macd_sign_cci_level_state"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "fast_length": [12, 8],
}
DEFAULT_PARAMS = {"length": 14, "fast_length": 12, "slow_length": 26}


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
    n = int(p["length"])
    ma = c.rolling(n).mean()
    dev = c.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        cci = (c - ma) / (0.015 * dev)
    macd = c.ewm(span=int(p["fast_length"]), adjust=False).mean() - c.ewm(span=int(p["slow_length"]), adjust=False).mean()
    lc = ((cci > 100) & (macd > 0)) | ((cci > -100) & (macd < 0))
    sc = ((cci < -100) & (macd < 0)) | ((cci < 100) & (macd > 0))
    false = pd.Series(False, index=c.index)
    return lc, false, sc, false.copy()


def portfolio_kwargs(**params):
    return {}
