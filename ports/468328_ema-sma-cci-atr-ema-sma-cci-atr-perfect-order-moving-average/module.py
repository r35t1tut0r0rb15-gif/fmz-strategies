"""Trend Magic colour turns in a perfect moving-average order, 5-minute bars: the CCI 21 turning to 0 or over with the EMA 45 over the SMA 90 over the SMA 180 goes long with a stop at the SMA 90 and a target 1.5 times that risk, the mirror goes short; reversing.
Port of FMZ strategy #468328 "EMA-SMA-CCI-ATR-均线完美排列策略与趋势魔法指标自动交易系统-EMA-SMA-CCI-ATR-Perfect-Order-Moving-Average-Strategy-with-Trend-Magic-Indicator-Auto-Trading-System" (Trend Magic with EMA, SMA, and Auto-Trading).

FMZ source id: 468328

Source
    https://www.fmz.com/strategy/468328 (PineScript v5, FMZ last modified 2024-09-26 15:52:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 136-223), CCI 21 sign (Trend Magic colour; the line itself only plotted); EMA 45, SMA 90 / 180; stop = SMA 90 of the signal bar, target = close +- 1.5 x the risk
    ema45 > sma90 > sma180 and crossover(isBlue, isRed) -> entry Buy, stop = sma90, limit = close + 1.5 x (close - sma90)
    ema45 < sma90 < sma180 and crossunder(isBlue, isRed) -> entry Sell, stop = sma90, limit = close - 1.5 x (sma90 - close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The colour turn is the CCI moving from under 0 to 0 or over (and back). The levels are prices
      fixed on the signal bar, sent as fractions of the fill open (the signal bar's levels shifted into
      the fill bar); a level already at or through the fill open is marketable and is sent as a
      bar-close exit on the fill bar (one bar late). REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar levels as fractions of the fill.
    2 generic: PASS, CCI sign turns in a perfect MA order with an SMA stop.
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

NAME = "fmz_468328_trend_magic_turn_perfect_order_sma90_stop_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "cci_period": [21, 14],
    "rr": [1.5, 3.0],
}
DEFAULT_PARAMS = {"cci_period": 21, "rr": 1.5}


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


def _cci(c, n):
    sma = c.rolling(n).mean()
    v = c.to_numpy(dtype=float)
    win = np.lib.stride_tricks.sliding_window_view(v, n)
    dev = np.full(len(v), np.nan)
    dev[n - 1:] = np.abs(win - win.mean(axis=1, keepdims=True)).mean(axis=1)
    return (c - sma) / (0.015 * pd.Series(dev, index=c.index))


def _parts(bars_df, p):
    c = bars_df["close"]
    cci = _cci(c, int(p["cci_period"]))
    turn_b = (cci >= 0) & ~(cci.shift(1) >= 0)     # isBlue / isRed are both 0 while the CCI is na
    turn_r = (cci < 0) & ~(cci.shift(1) < 0)
    e45, s90, s180 = c.ewm(span=45, adjust=False).mean(), c.rolling(90).mean(), c.rolling(180).mean()
    le = (e45 > s90) & (s90 > s180) & turn_b
    se = (e45 < s90) & (s90 < s180) & turn_r
    rr = float(p["rr"])
    sl = s90.where(le | se)
    tp = (c + (c - s90) * rr).where(le, (c - (s90 - c) * rr).where(se))
    return le, se, sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, sl, tp = _parts(bars_df, p)
    o = bars_df["open"]
    was_l, was_s = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    s1, t1 = sl.shift(1), tp.shift(1)
    lx = was_l & ((s1 >= o) | (t1 <= o)) & ~se   # a level through the fill: closed at the next open
    sx = was_s & ((s1 <= o) | (t1 >= o)) & ~le
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, sl, tp = _parts(bars_df, p)
    o = bars_df["open"]
    was_l = le.shift(1, fill_value=False)
    s1, t1 = sl.shift(1), tp.shift(1)                         # the signal bar's levels, read at the fill
    sl_f = (1 - s1 / o).where(was_l, s1 / o - 1)
    tp_f = (t1 / o - 1).where(was_l, 1 - t1 / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
