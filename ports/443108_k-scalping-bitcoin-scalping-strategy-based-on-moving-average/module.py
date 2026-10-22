"""SMA 9 / 15 crossings on a steep slow SMA with a strong body, 2-hour bars, long only: the SMA 9 crossing over the SMA 15 with the slow SMA's one-bar slope angle at 30 degrees or more and a marubozu or
full-body bar goes long. The 0.5 % bracket is re-sent every bar from that bar's close and is kept pending, so the port has no exit.
Port of FMZ strategy #443108 "基于移动平均线交叉和K线形态的比特币scalping策略Bitcoin-Scalping-Strategy-Based-on-Moving-Average-Crossover-and-Candlestick-Patterns" (Moving Average Crossover Strategy with Candlestick Patterns).

FMZ source id: 443108

Source
    https://www.fmz.com/strategy/443108 (PineScript v4, FMZ last modified 2024-02-29 12:01:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 175-232), SMA 9 / 15; stop 0.5 %, target 0.5 %; angle 30 degrees
    ma_angle = abs(180 atan(sma15[1] - sma15) / 3.14159);  buy = crossover(sma9, sma15) and angle >= 30 and (pin bar or marubozu or full body) -> entry Buy
    exit(stop = close (1 - 0.5 %), limit = close (1 + 0.5 %)) every bar;  sell signal plots only

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pin-bar test can never hold (its tails compare the body top with the high the wrong way), so
      marubozu or full body decide. Criterion 2: the angle takes atan of a price difference: the port
      scales the difference to the close at the BTC reading of 42000 (x 42000 / close). The bracket is
      re-sent on every bar from that bar's close, so its levels move after entry: stops() cannot express
      a level re-set every bar, so it is described here and kept pending (as #438034, mark
      trailing_stop_pending); without it the port has no exit (as #437800). The sell signal only plots.
      Long only. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the per-bar bracket described (pending).
    2 generic: ADAPT, price-unit slope angle -> scaled to the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG443108 (2 members, best partner #443109, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_443108_sma9_15_cross_steep_slope_body_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "angle": [30, 60],
}
DEFAULT_PARAMS = {"fast": 9, "angle": 30, "slow": 15, "ref_price": 42000.0}


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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    slope = (s.shift(1) - s) * float(p["ref_price"]) / c
    ang = (180 * np.arctan(slope) / 3.14159).abs()
    body, body1 = (o - c).abs(), (o.shift(1) - c.shift(1)).abs()
    maru = (body > body1 * 0.75) & (h == np.maximum(o, c)) & (lo == np.minimum(o, c))
    full = body > body1 * 0.95
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (ang >= float(p["angle"])) & (maru | full)
    false = pd.Series(False, index=c.index)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
