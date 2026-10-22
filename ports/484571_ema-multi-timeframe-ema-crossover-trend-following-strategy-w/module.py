"""EMA 5 crossing both EMA 8 and EMA 13 on one bar, 1-minute bars: the up-cross goes long, the down-cross goes short, each followed by a trail 10 % behind the best high / low (the input's 0.10 used as a fraction, as written); reversing.
Port of FMZ strategy #484571 "多重时框EMA交叉趋势跟踪策略结合支阻力与智能追踪止损系统-Multi-Timeframe-EMA-Crossover-Trend-Following-Strategy-with-Support-Resistance-and-Smart-Trailing-Stop-System" (EMA Crossover Strategy with S/R and Cross Exits v6).

FMZ source id: 484571

Source
    https://www.fmz.com/strategy/484571 (PineScript v6, FMZ last modified 2025-03-03 09:25:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 182-260), EMA 5 / 8 / 13; trail offset input 0.10 "%" used as 0.10; hourly high[1] / low[1] with lookahead_on (plots only)
    crossover(ema5, ema8) and crossover(ema5, ema13) -> entry Long, close Short;  crossunder both -> entry Short, close Long
    long: maxHigh = max(high since entry), longStop = max(longStop, maxHigh x (1 - 0.10));  exit Long (stop = longStop);  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written (intended version owed): the "%" input 0.10 multiplies the price directly, so the trail
      sits 10 % behind the best price. It ratchets on the highest high since the fill bar (the lowest low
      for shorts): the house percent trail pct 0.10 on the best high / low (anchor high_low); mark
      trailing_stop. The hourly support / resistance levels use lookahead_on but feed only plots, so they
      are not ported. An entry on the other side reverses (REVERSAL INTENDED). Stop module:
      portfolio_kwargs {} (driver D4). No sizing code (margin 100 / 100). FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; house percent trail.
    2 generic: PASS, triple EMA crossings with a percent trail.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_484571_ema5_cross_ema8_13_pct_trail_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_offset": [0.1, 0.01],
    "ema_fast": [5, 3],
}
DEFAULT_PARAMS = {"trail_offset": 0.1, "ema_fast": 5, "ema_mid": 8, "ema_slow": 13}


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
    e5 = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    e8 = c.ewm(span=int(p["ema_mid"]), adjust=False).mean()
    e13 = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    le = (e5 > e8) & (e5.shift(1) <= e8.shift(1)) & (e5 > e13) & (e5.shift(1) <= e13.shift(1))
    se = (e5 < e8) & (e5.shift(1) >= e8.shift(1)) & (e5 < e13) & (e5.shift(1) >= e13.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_offset"]), "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
