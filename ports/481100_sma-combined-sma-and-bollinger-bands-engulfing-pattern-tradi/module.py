"""Engulfing-style candles on the SMA 200 and BB 14 basis side, 3-hour bars: a bullish one above both goes long with a stop at its low and a 2 R target, a bearish one below both goes short with a stop at its high; reversing.
Port of FMZ strategy #481100 "基于SMA和布林带的吞没形态指标组合交易策略-Combined-SMA-and-Bollinger-Bands-Engulfing-Pattern-Trading-Strategy" (Engulfing Candles Strategy with Risk-Reward 1:2).

FMZ source id: 481100

Source
    https://www.fmz.com/strategy/481100 (PineScript v5, FMZ last modified 2025-02-08 15:06:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-175), SMA 200; BB 14 / 2 (basis used); stop at the candle's low / high; R:R 1:2
    open <= close[1] and open < open[1] and close > open[1] and close > sma200 and close > basis14 -> entry Buy + exit(stop = low, limit = close + 2 (close - low)), close Sell
    open >= close[1] and open > open[1] and close < open[1] and close < sma200 and close < basis14 -> entry Sell + exit(stop = high, limit = close - 2 (high - close)), close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on each signal bar from its low / high and close: the opening signal's levels
      are ported, sent as fractions of the fill open (a level at or through it is marketable and closed
      one bar late, as #458256); a repeat signal inside a trade re-sends it, which is not followed (as
      #434428, mark trailing_stop_pending). Each signal also closes the other side, which is the reversal.
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour:
      mark coarse_bar_stop. No sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar candle bracket as fractions of the fill.
    2 generic: PASS, engulfing-style candles with SMA 200 / BB basis filters and a 2 R bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_481100_engulf_style_sma200_bb14_basis_2r_bracket_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [2.0, 1.0],
    "bb_length": [14, 20],
}
DEFAULT_PARAMS = {"rr": 2.0, "bb_length": 14, "sma_length": 200}


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


def _signals(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    sma = c.rolling(int(p["sma_length"])).mean()
    mid = c.rolling(int(p["bb_length"])).mean()
    bull = (o <= c.shift(1)) & (o < o.shift(1)) & (c > o.shift(1))
    bear = (o >= c.shift(1)) & (o > o.shift(1)) & (c < o.shift(1))
    le = bull & (c > sma) & (c > mid)
    se = bear & (c < sma) & (c < mid)
    rr = float(p["rr"])
    lvl = {"l_sl": lo, "l_tp": c + rr * (c - lo), "s_sl": h, "s_tp": c - rr * (h - c)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
