"""RSI 12 momentum, 1-hour bars: RSI above 70 goes long, under 30 goes short (the default "overbought go long" mode).
Port of FMZ strategy #431498 "RSI双向突破策略RSI-Reversal-Breakout-Strategy" (RSI Strategy (REV0LUTI0N)).

FMZ source id: 431498

Source
    https://www.fmz.com/strategy/431498 (PineScript v4, FMZ last modified 2023-11-08 12:11:03).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 197-291), RSI 12, 70 / 30, normal mode, no EMA filter, SL / TP off
    xRSI > 70 (rsinormal, no EMA filter) -> entry long;  xRSI < 30 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The defaults: "Overbought Go Long" on, EMA filter off, the entry time frame "" (always), the
      end-of-window close, stop and target off. Entries are re-issued while the condition holds.
      strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10000 cash per order stored in original_sizing.txt.
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

NAME = "fmz_431498_rsi_momentum_reverse"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [12, 24],
    "overbought": [70, 60],
}
DEFAULT_PARAMS = {"length": 12, "overbought": 70}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r = _rsi(bars_df["close"], int(p["length"]))
    ob = float(p["overbought"])
    lg = (r > ob).astype(bool)
    sh = (r < 100 - ob).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def portfolio_kwargs(**params):
    return {}
