"""Open-at-the-extreme candles, 1-hour bars: a bar opening at its low goes long, a bar opening at its high goes short; reversing (with the stop lines hidden the stop and target are na, so the exit tests
never fire).
Port of FMZ strategy #440817 "Open High Close Low Breakout Trading Strategy" (OLH).

FMZ source id: 440817

Source
    https://www.fmz.com/strategy/440817 (PineScript v5, FMZ last modified 2024-02-02 12:03:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 154-218), ATR 14 for the stop (shown only when "Show SL lines" is on, off by default); risk:reward 2; markets always on; lot 1
    longCond = open == low -> entry enter long, sl := longStop (na when the lines are hidden), target := close + (close - sl) x 2;  shortCond = open == high -> entry enter short (mirrored)
    close >= target or close <= sl -> close enter long;  close <= target or close >= sl -> close enter short

Interpretation choices (Pine rules in SURVEY_README.md)
    * longStop and shortStop are na unless the "Show SL lines" input is on (off by default), so sl and
      target are na and the close tests are never true: positions end at the opposite entry. The short
      entry is written after the long one and wins on a bar opening at both its high and low (as
      #437773). strategy.entry reverses: REVERSAL INTENDED. The lot size is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, open at the bar's extreme.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: lot size is sizing.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: DG440817 (2 members, best partner #441989, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (markets-always-on input).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440817_open_at_extreme_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tol_frac": [0.0],
}
DEFAULT_PARAMS = {"tol_frac": 0.0}


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
    o, h, lo = bars_df["open"], bars_df["high"], bars_df["low"]
    t = float(p["tol_frac"]) * o
    lg = (o - lo) <= t
    sh = (h - o) <= t
    false = pd.Series(False, index=o.index)
    return lg & ~sh, false, sh, false.copy()


def portfolio_kwargs(**params):
    return {}
