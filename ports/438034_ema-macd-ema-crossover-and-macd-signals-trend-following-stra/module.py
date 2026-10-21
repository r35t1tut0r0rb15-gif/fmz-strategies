"""EMA 9 / 21 crossings with the close on the same side of the EMA 21, 1-hour bars: the cross up with the close above goes long, the cross down with the close below goes short; reversing. The long's 1 % / 2 %
bracket is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #438034 "基于EMA均线和MACD指标的趋势跟踪策略EMA-Crossover-and-MACD-Signals-Trend-Following-Strategy" (EMA Crossover and Close Above/Below EMA 21).

FMZ source id: 438034

Source
    https://www.fmz.com/strategy/438034 (PineScript v5, FMZ last modified 2024-01-08 14:31:56).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 135-160), EMA 9 / 21; stop 1 %, target 2 % of the current close
    buy = crossover(ema 9, ema 21) and close > ema 21 -> entry Buy;  sell = crossunder and close < ema 21 -> entry Sell;  every bar: exit(from Buy, stop = close x 0.99, limit = close x 1.02)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long's bracket is re-sent on every bar from that bar's close, so its levels move after entry
      (a stop 1 % under and a target 2 % over the latest close, active for the next bar): stops() cannot
      express a level re-set every bar, so it is described here and kept pending (as #437036, mark
      trailing_stop_pending). Positions end at the opposite entry until then; shorts have no exit in the
      source. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_438034_ema9_21_cross_close_side"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1)) & (c > s)
    dn = (f < s) & (f.shift(1) >= s.shift(1)) & (c < s)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
