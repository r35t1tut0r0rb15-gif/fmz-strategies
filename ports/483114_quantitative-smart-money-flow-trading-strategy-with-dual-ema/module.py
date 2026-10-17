"""Order-block bars two bars back in the EMA 50 / 200 trend, with the 5-bar extreme as the stop and a 2 R target,
1-hour bars: with EMA 50 above EMA 200, a green bar two bars ago whose low was the 5-bar low goes long (stop the
current 5-bar low, target close + 2 x (close - stop)); the mirror goes short.
Port of FMZ strategy #483114 "基于双均线和动态订单块检测的智能资金流量化交易策略-Quantitative-Smart-Money-Flow-Trading-Strategy-with-Dual-EMA-and-Dynamic-Order-Block-Detection" (XAU/EUR Beginner-Friendly Strategy).

FMZ source id: 483114

Source
    https://www.fmz.com/strategy/483114 (PineScript v5, FMZ last modified 2025-02-21 14:10:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 96-150), EMA 50 / 200, RR 2, swing window 5
    bullish block = low[2] == lowest(low, 5)[2] and close[2] > open[2]; long = ema50 > ema200 and bullish block
    stop = lowest(low, 5), limit = close + (close - stop) x 2 (short mirrored with the highs)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: sl = (close - lowest low 5) / close, tp = rr x sl
      ((highest high 5 - close) / close for a short), picked by the signal's side, shifted one bar inside stops() and
      re-based on the fill (house rule). A signal whose stop is not beyond the close (zero-length trade) emits no entry
      (as #490798). A same-side signal while held re-places it: mark trailing_stop_pending.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest
      header ("XAU/EUR" in the title is a label).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, moving averages and rolling swing extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_483114_order_block_ema50_200_swing_bracket"
FAMILY = "price_action"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [2.0, 3.0],
    "swing_len": [5, 10],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200, "rr": 2.0, "swing_len": 5}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    n = int(p["swing_len"])
    sh, sl_ = h.rolling(n).max(), lo.rolling(n).min()
    bull = (lo.shift(2) == sl_.shift(2)) & (c.shift(2) > o.shift(2))
    bear = (h.shift(2) == sh.shift(2)) & (c.shift(2) < o.shift(2))
    d_long, d_short = (c - sl_) / c, (sh - c) / c
    long_e = ((f > s) & bull & (d_long > 0)).astype(bool)
    short_e = ((f < s) & bear & (d_short > 0)).astype(bool)
    return long_e, short_e, d_long, d_short


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, _, d_long, d_short = _signals(bars_df, p)
    sl = d_long.where(long_e, d_short)
    return {"sl_stop": sl.shift(1), "tp_stop": (p["rr"] * sl).shift(1)}


def portfolio_kwargs(**params):
    return {}
