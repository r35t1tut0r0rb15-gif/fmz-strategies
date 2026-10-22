"""Kalman-filtered close slope angles, 15-minute bars: when the 30-bar sum of the filter's slope angles exceeds 360 degrees the script goes long, below -360 short; reversing; the slope is read on a BTC price
scale.
Port of FMZ strategy #439972 "Kalman Filter Based Trend Tracking Strategy" (策略360°（测试）).

FMZ source id: 439972

Source
    https://www.fmz.com/strategy/439972 (PineScript v5, FMZ last modified 2024-01-25 14:12:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 167-216), 1-minute SMA 1 via security; Kalman gain 0.01; angle sum over 30 bars; thresholds +/- 360
    ma1 = security("1", sma(close, 1));  kf: dk = x - kf[1], smooth = kf[1] + dk sqrt(2g), velo += g dk, kf = smooth + velo;  angle = degrees(atan(kf - kf[1]));  sum_angle = sum(angle, 30)
    buy = sum_angle > 360 -> entry Long, close Short;  sell = sum_angle < -360 -> entry Short, close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * A 1-minute value requested from a 15-minute chart is its last minute inside the bar (as #436765):
      the bar's close. Criterion 2: atan of a raw price difference depends on the price scale; the port
      takes atan(difference / close x 42000), the BTC reading near 42000. The closes share the
      reversing entry's bar and change nothing. strategy.entry reverses: REVERSAL INTENDED. No sizing
      code. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 1-minute value is the bar close.
    2 generic: ADAPT, price-scale slope angle -> angle of the slope on a BTC scale.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG439972 (2 members, best partner #440827, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439972_kalman_slope_angle_sum"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "scale": [42000.0, 4200.0],
    "period": [30, 15],
}
DEFAULT_PARAMS = {"scale": 42000.0, "period": 30, "gain": 0.01, "limit": 360.0}


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
    x = c.to_numpy(dtype=float)
    g = float(p["gain"])
    m = len(x)
    kf = np.full(m, np.nan)
    velo = 0.0
    for i in range(m):
        base = kf[i - 1] if i > 0 and not np.isnan(kf[i - 1]) else x[i]
        dk = x[i] - base
        velo = velo + g * dk
        kf[i] = base + dk * np.sqrt(g * 2) + velo
    k = pd.Series(kf, index=c.index)
    ang = np.degrees(np.arctan((k - k.shift(1)) / c * float(p["scale"])))
    s = ang.rolling(int(p["period"])).sum()
    lim = float(p["limit"])
    false = pd.Series(False, index=c.index)
    return s > lim, false, s < -lim, false.copy()


def portfolio_kwargs(**params):
    return {}
