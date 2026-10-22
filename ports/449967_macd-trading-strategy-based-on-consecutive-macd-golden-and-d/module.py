"""MACD (12, 26, 9) signal crossings, 1-hour bars, with a 1 % bracket: a cross up goes long, a cross down goes short, each with a 1 % stop and a 1 % target from the signal close; reversing.
Port of FMZ strategy #449967 "基于连续MACD金叉死叉的交易策略-Trading-Strategy-Based-on-Consecutive-MACD-Golden-and-Death-Crosses" (连续MACD交叉和回测范围 (consecutive MACD crosses)).

FMZ source id: 449967

Source
    https://www.fmz.com/strategy/449967 (PineScript v5, FMZ last modified 2024-04-30 17:26:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-153), MACD 12 / 26 / 9; long / short TP and SL 0.01 each; date filter (always true)
    crossUp -> lastCrossUp = true;  lastCrossUp and crossUp -> entry 买入开多, exit(limit = close x 1.01, stop = close x 0.99);  crossDown mirrored -> entry 卖出开空

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "consecutive" flag is set on the crossing bar before it is tested, so every crossing trades,
      as written. The bracket is a fixed 1 % of the signal close, ported as fractions of the fill (as
      #437751); crossings alternate, so a trade never sees a repeated signal. REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, MACD signal crossings with a percent bracket.
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

NAME = "fmz_449967_macd_cross_one_pct_bracket_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.01, 0.02],
    "sl": [0.01, 0.005],
}
DEFAULT_PARAMS = {"tp": 0.01, "sl": 0.01, "fast": 12, "slow": 26, "signal": 9}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    se = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
