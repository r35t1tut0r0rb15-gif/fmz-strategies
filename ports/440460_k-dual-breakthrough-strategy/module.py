"""Inside-pause breakout candles, 1-hour bars: a green candle closing above both the close and open two bars back, after a bar with a lower high and lower low than the one before, goes long; the bearish
mirror goes short; reversing (the stop and target modes default to None).
Port of FMZ strategy #440460 "基于K线的双向突破交易策略Dual-Breakthrough-Strategy" (Strategy Template Autoview).

FMZ source id: 440460

Source
    https://www.fmz.com/strategy/440460 (PineScript v5, FMZ last modified 2024-01-30 17:27:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 189-487), stop mode None, target mode None; 2 contracts; process orders on close; date filter off
    bull = close > open and close > max(close[2], open[2]) and low[1] < low[2] and high[1] < high[2];  bear = close < open and close < min(close[2], open[2]) and low[1] > low[2] and high[1] > high[2]
    bull -> entry Long, else bear -> entry Short;  strategy.exit with stop / limit na (modes None)

Interpretation choices (Pine rules in SURVEY_README.md)
    * process_orders_on_close fills orders on the signal bar's close; the house fills at the next open
      (the one fill convention), which equals that close apart from gaps. calc_on_every_tick only matters
      in real time. With both modes None the exit calls carry no levels and place nothing. The Autoview
      alert texts are not ported. strategy.entry reverses: REVERSAL INTENDED. The 2 contracts, capital and
      commission are sizing and costs. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders (house fill at the next open).
    2 generic: PASS, candle pattern.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: contracts, capital and commission settings.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440460_inside_pause_breakout_candles"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lag": [2, 3],
}
DEFAULT_PARAMS = {"lag": 2}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    k = int(p["lag"])
    ck, ok_, hk, lk = c.shift(k), o.shift(k), h.shift(k), lo.shift(k)
    bull = (c > o) & (c > np.maximum(ck, ok_)) & (lo.shift(1) < lk) & (h.shift(1) < hk)
    bear = (c < o) & (c < np.minimum(ck, ok_)) & (lo.shift(1) > lk) & (h.shift(1) > hk)
    false = pd.Series(False, index=c.index)
    return bull, false, bear & ~bull, false.copy()


def portfolio_kwargs(**params):
    return {}
