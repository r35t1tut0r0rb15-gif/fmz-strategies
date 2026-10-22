"""Engulfing-style closes on the EMA 20 side, hourly bars: a close above the previous open after opening below the previous close, above the EMA, goes long; the mirror below goes short; reversing. The 1 % / 1.5 % bracket is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #478736 "EMA趋势结合轮回位突破交易策略-EMA-Trend-with-Round-Number-Breakout-Trading-Strategy" (The Gold Box Strategy).

FMZ source id: 478736

Source
    https://www.fmz.com/strategy/478736 (PineScript v6, FMZ last modified 2025-01-17 16:17:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-150), EMA 20; round-number interval 5 (unused); sessions computed, filter fixed true; stop 1 %, target 1.5 % of the current close; 200 % of equity
    close > open[1] and open < close[1] and close > ema20 -> entry Long;  close < open[1] and open > close[1] and close < ema20 -> entry Short;  every bar: exit(Long / Short, stop = close x (1 -/+ 1 %), limit = close x (1 +/- 1.5 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "engulfing" tests compare with the previous candle's open and close, with no colour test, as
      written. The session flag is fixed true and the round-number levels are unused. The bracket is
      re-sent on every bar from that bar's close, so its levels move after entry: stops() cannot express
      a level re-set every bar, so it is described here and kept pending (as #438034, mark
      trailing_stop_pending). REVERSAL INTENDED. The 200 % of equity size is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar bracket described (pending).
    2 generic: PASS, engulfing-style closes on the EMA side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity stored, not ported; the bracket inputs stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (session filter fixed true).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_478736_engulf_style_ema20_side_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [20, 50],
}
DEFAULT_PARAMS = {"ema_length": 20}


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
    o, c = bars_df["open"], bars_df["close"]
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    le = (c > o.shift(1)) & (o < c.shift(1)) & (c > e)
    se = (c < o.shift(1)) & (o > c.shift(1)) & (c < e)
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
