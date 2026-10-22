"""Recent SMA 8 / 21 crossings confirmed by the SMA 21's ATR-normalised angle, 10-minute bars: a cross up within the last 15 bars with the SMA 21 angle above 7 degrees goes long, a cross down with the angle
below -7 goes short; reversing.
Port of FMZ strategy #439106 "8周期和21周期的移动平均线策略Dual-Moving-Average-Strategy" (Dual Moving Average).

FMZ source id: 439106

Source
    https://www.fmz.com/strategy/439106 (PineScript v4, FMZ last modified 2024-01-17 17:45:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 167-208), SMA 8 / 21; angle 7; angle period 2; ATR 10; look-back 15 (angle level 6 unused)
    angle = degrees(atan((sma21 - sma21[2]) / atr(10) / 2));  crossed = crossover(sma 8, sma 21) on any of the last 15 bars (not the current one)
    long = crossed up and angle > 7 -> entry Long;  short = crossed down and angle < -7 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The look-back counts bars 1 to 15 back, so the current bar's cross is not included, as written. The
      conditions are states, so the entries are sent on every qualifying bar. strategy.entry reverses:
      REVERSAL INTENDED. The capital is sizing. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA crossings and an ATR-normalised slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital stored.
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

NAME = "fmz_439106_sma8_21_cross_angle"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "angle": [7, 3],
    "lookback": [15, 5],
}
DEFAULT_PARAMS = {"angle": 7.0, "lookback": 15, "angle_period": 2, "atr_period": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ma1, ma2 = c.rolling(8).mean(), c.rolling(21).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_period"]))
    k = int(p["angle_period"])
    with np.errstate(divide="ignore", invalid="ignore"):
        ang = np.degrees(np.arctan((ma2 - ma2.shift(k)) / atr / k))
    xo = ((ma1 > ma2) & (ma1.shift(1) <= ma2.shift(1))).astype(float)
    xu = ((ma1 < ma2) & (ma1.shift(1) >= ma2.shift(1))).astype(float)
    lb = int(p["lookback"])
    long_x = xo.shift(1).rolling(lb, min_periods=1).max() > 0
    short_x = xu.shift(1).rolling(lb, min_periods=1).max() > 0
    a = float(p["angle"])
    up = long_x & (ang > a)
    dn = short_x & (ang < -a)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
