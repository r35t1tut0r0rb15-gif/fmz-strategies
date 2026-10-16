"""EMA 20 / 50 cross with an EMA 200 trend filter and a 1 % bracket, 2-hour bars: the up cross above the EMA 200
goes long, the down cross below it goes short; each trade has a 1 % stop and a 1 % target.
Port of FMZ strategy #428985 "Swing Trading Strategy" (Bozz Strategy).

FMZ source id: 428985

Source
    https://www.fmz.com/strategy/428985 (PineScript v4, FMZ last modified 2023-10-11 16:29:37).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 170-230), EMA 20 / 50, trend EMA 200, stop / target 1 %, swing mode off
    crossover(ema20, ema50) and close > ema200 -> entry long; crossunder(ema20, ema50) and close < ema200 -> entry short
    exit(limit = avg x (1 +/- 1 %), stop = avg x (1 -/+ 1 %)) per side (swing_trading_mode false)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source MA (EMA 50) is plotted only. Leverage and the quantity are sizing. The trading window
      is always true.
    * The bracket is 1 % of the average entry price (the fill): sl_stop / tp_stop 0.01.
    * strategy.entry reverses an open position on the opposite cross. Stop module: portfolio_kwargs {}
      (driver D4); REVERSAL INTENDED. Stops on 2-hour bars: mark coarse_bar_stop. FREQ = "2h".

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, moving-average crosses and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy(), leverage and quantity stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG428985 (2 members, best partner #433915, Jaccard 0.839); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_428985_ema20_50_trend_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [1.0, 2.0],
    "tp_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50, "trend": 200, "sl_pct": 1.0, "tp_pct": 1.0}


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
    e = lambda n: c.ewm(span=int(n), adjust=False).mean()  # noqa: E731
    f, s, t = e(p["fast"]), e(p["slow"]), e(p["trend"])
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > t)).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (c < t)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100, "tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
