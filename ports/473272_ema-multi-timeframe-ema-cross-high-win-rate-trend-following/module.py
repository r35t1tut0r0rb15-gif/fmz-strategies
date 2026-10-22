"""Close crossings over the EMA 20 in a stacked EMA 20 / 50 / 200 uptrend, hourly bars, long only. The 10 % / 5 % bracket is set from the position price on the signal bar, which is na from flat, so it is armed only by a repeat signal inside a trade: not ported (pending), no exit.
Port of FMZ strategy #473272 "多周期EMA交叉高胜率趋势跟踪策略进阶版-Multi-Timeframe-EMA-Cross-High-Win-Rate-Trend-Following-Strategy-Advanced" (EMA Cross Strategy with Targets and Fill).

FMZ source id: 473272

Source
    https://www.fmz.com/strategy/473272 (PineScript v5, FMZ last modified 2024-11-28 17:27:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 128-180), EMA 20 / 50 / 200 (constants); target avg x 1.10, stop avg x 0.95 set on signal bars, exit sent every bar
    crossover(close, ema20) and ema20 > ema50 > ema200 -> entry Buy, tp := avg x 1.10, sl := avg x 0.95;  every bar: exit(Buy, limit = tp, stop = sl)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.position_avg_price on the signal bar is na from flat, so the levels of a new trade are
      na; only a repeat signal inside the trade sets real ones. A bracket armed only by repeat signals
      is not ported (as #437800): kept pending (mark trailing_stop_pending), so the port has no exit.
      Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA 20 cross-ups in a stacked uptrend; bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket stored.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473272_close_cross_ema20_stacked_trend_long_bracket_pending"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    c = bars_df["close"]
    e20, e50, e200 = (c.ewm(span=n, adjust=False).mean() for n in (20, 50, 200))
    le = (c > e20) & (c.shift(1) <= e20.shift(1)) & (e20 > e50) & (e50 > e200)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
