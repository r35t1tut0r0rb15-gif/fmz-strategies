"""Smoothed Heikin-Ashi close (EMA 6) crossing the SMA 44, hourly bars: the cross up goes long, the cross down goes short; reversing. A position is closed when the smoothed close is within 0.001 (in price) of the SMA.
Port of FMZ strategy #473398 "平滑型Heikin-Ashi结合SMA交叉趋势跟踪策略-Smoothed-Heikin-Ashi-with-SMA-Crossover-Trend-Following-Strategy" (Smoothed Heikin Ashi with SMA Strategy).

FMZ source id: 473398

Source
    https://www.fmz.com/strategy/473398 (PineScript v5, FMZ last modified 2024-11-29 16:39:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-134), SMA 11 (plotted only) / 44; smoothing EMA 6; no-position band 0.001 in price
    crossover(ema6(haClose), sma44) -> entry Long;  crossunder -> entry Short;  |ema6(haClose) - sma44| < 0.001 and in a position -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * haOpen (a recursion) and the smoothed open / high / low only feed the plotted candles; the
      smoothed close (EMA 6 of (O + H + L + C) / 4) is all that reaches the orders. The 0.001 band is a price amount, ported as a fraction of 42000 of the close
      (2.4e-8). close_all acts only on the position held into the bar and not reversed on it
      (#437773), so it is masked on entry bars. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed Heikin-Ashi crossings of an SMA.
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

NAME = "fmz_473398_smoothed_heikin_ashi_close_cross_sma44_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_long": [44, 100],
    "smooth": [6, 12],
}
DEFAULT_PARAMS = {"sma_long": 44, "smooth": 6, "band_frac": 2.381e-08}  # 0.001 in price / 42000


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
    hc = (o + h + lo + c) / 4
    sc = hc.ewm(span=int(p["smooth"]), adjust=False).mean()
    ma = c.rolling(int(p["sma_long"])).mean()
    le = (sc > ma) & (sc.shift(1) <= ma.shift(1))
    se = (sc < ma) & (sc.shift(1) >= ma.shift(1))
    flat = ((sc - ma).abs() < float(p["band_frac"]) * c) & ~le & ~se
    return le, flat, se, flat.copy()


def portfolio_kwargs(**params):
    return {}
