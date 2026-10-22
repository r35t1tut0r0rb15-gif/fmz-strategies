"""Hammer-shaped candles, hourly bars: a green small-body candle with a long lower shadow goes long, a red one goes short; a position closes 26 bars after its entry bar; reversing.
Port of FMZ strategy #477960 "双时间框架趋势反转K线形态量化交易策略-Dual-Timeframe-Trend-Reversal-Candlestick-Pattern-Quantitative-Trading-Strategy" (Hammer and Hanging Man Strategy).

FMZ source id: 477960

Source
    https://www.fmz.com/strategy/477960 (PineScript v6, FMZ last modified 2025-01-10 15:47:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-149), body <= range / 5; lower shadow >= body x 1; upper shadow <= body; hold 26 bars
    small body, long lower shadow, short upper shadow and close > open -> entry Long;  the same and close < open -> entry Short;  held and bar_index - entry_bar_index(0) >= 26 -> close Long / Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both patterns have the same shape and differ only in colour. A loop counts the bars from each
      position's fill bar and closes at the next open from the 26th; a reversal starts a new count, a
      repeat on the held side does not, and a close on the bar of a same-side repeat ends the trade (as
      #472251) while a same-bar reversal stands. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, hammer-shaped candles with a fixed holding time.
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

NAME = "fmz_477960_hammer_shape_colour_hold26_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hold_periods": [26, 12],
    "length": [5, 3],
}
DEFAULT_PARAMS = {"hold_periods": 26, "length": 5, "shadow_ratio": 1.0}


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
    body = (c - o).abs()
    lower = pd.concat([o, c], axis=1).min(axis=1) - lo
    upper = h - pd.concat([o, c], axis=1).max(axis=1)
    shape = (body <= (h - lo) / int(p["length"])) & (lower >= body * float(p["shadow_ratio"])) & (upper <= body)
    lc = (shape & (c > o)).to_numpy()
    sc = (shape & (c < o)).to_numpy()
    k = int(p["hold_periods"])
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt, fill = 0, 0, -1
    for i in range(m):
        if nxt != pos and nxt != 0:
            fill = i
        pos = nxt
        if lc[i] and pos != 1:
            le[i], nxt = True, 1
        if sc[i] and pos != -1:
            se[i], nxt = True, -1
        if pos == 1 and not se[i] and i - fill >= k:
            lx[i], nxt = True, 0
        if pos == -1 and not le[i] and i - fill >= k:
            sx[i], nxt = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
