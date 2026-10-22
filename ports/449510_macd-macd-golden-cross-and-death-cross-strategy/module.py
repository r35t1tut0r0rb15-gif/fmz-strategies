"""MACD (12, 26, 9) signal crossings, 1-hour bars, long only: the DIF crossing over its EMA goes long, crossing under closes.
Port of FMZ strategy #449510 "MACD金叉死叉策略-MACD-Golden-Cross-and-Death-Cross-Strategy" (MACD 金叉策略 (MACD golden-cross strategy)).

FMZ source id: 449510

Source
    https://www.fmz.com/strategy/449510 (PineScript v5, FMZ last modified 2024-04-26 12:08:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 109-178), MACD 12 / 26 / 9; entry ids numbered by round
    crossunder(DIF, EDA) -> close "long round n";  crossover(DIF, EDA) -> round + 1, entry "long round n+1"

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each round names its own entry id and the close names the current round's id, so it closes the
      open long; the short helpers are never called. Long only. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD signal crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449510_macd_signal_cross_rounds_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 21],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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
    dif = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    eda = dif.ewm(span=int(p["signal"]), adjust=False).mean()
    le = (dif > eda) & (dif.shift(1) <= eda.shift(1))
    lx = (dif < eda) & (dif.shift(1) >= eda.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
