"""One-minute bars: a price "predicted" from volume by a 21-bar regression of close on volume crossing over its WMA 9, with that prediction's MACD rising and above its signal, goes long; a falling prediction MACD under its signal with two lower lows goes short; reversing.
Port of FMZ strategy #435270 "Dynamic Pattern Trend Reversal Strategy" (Linear Cross (stocktechbot)).

FMZ source id: 435270

Source
    https://www.fmz.com/strategy/435270 (PineScript v5, FMZ last modified 2023-12-13 16:52:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 120-204), regression length 21 (close on volume); WMA 9 of the prediction; MACD 12 / 26 / 9 of the prediction
    [a, b] = linregs(close, volume, 21);  predicted = a + b x volume;  [macdLine, signalLine] = ta.macd(predicted, 12, 26, 9)
    crossover(predicted, wma(predicted, 9)) and signalLine < macdLine and rising(macdLine, 2) -> entry long;  falling(macdLine, 1) and macdLine < signalLine and falling(low, 2) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The prediction is in price units whatever the volume's units (the slope scales inversely), so the
      regression is unit-free. ta.rising(x, 2) is read as above both previous values, ta.falling(x, 1) as
      under the previous value (as earlier ports). The SMA conditions and the days-since-entry lines feed
      no order. margin_short 0 does not block shorts. REVERSAL INTENDED. margin settings are sizing. FREQ =
      "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume-regression price prediction crossings with a MACD filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): margin_long 100, margin_short 0, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG435270 (2 members, best partner #446331, Jaccard 0.977); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the regressor of the 21-bar close-on-volume regression; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435270_volume_regression_prediction_wma_cross_macd_1m_reversal"
FAMILY = "volume_regression"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 50],
    "linear_len": [9, 20],
}
DEFAULT_PARAMS = {"length": 21, "linear_len": 9}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _predicted(c, v, n):
    """The source's linregs(close, volume, n): each bar's deviation from that bar's own n-bar means,
    summed over n bars (series arithmetic, as Pine evaluates it), then a + b x volume."""
    yb, xb = c.rolling(n).mean(), v.rolling(n).mean()
    den = ((v - xb) ** 2).rolling(n).sum()
    b = ((v - xb) * (c - yb)).rolling(n).sum() / den.where(den != 0)
    return yb - b * xb + b * v


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lo, c, v = bars_df["low"], bars_df["close"], bars_df["volume"]
    pr = _predicted(c, v, int(p["length"]))
    macd = _ema(pr, 12) - _ema(pr, 26)
    sig = _ema(macd, 9)
    w = _wma(pr, int(p["linear_len"]))
    cross = (pr > w) & (pr.shift(1) <= w.shift(1))
    long_c = cross & (sig < macd) & (macd > macd.shift(1)) & (macd > macd.shift(2))
    short_c = (macd < macd.shift(1)) & (macd < sig) & (lo < lo.shift(1)) & (lo < lo.shift(2))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return long_c & ~short_c, false, short_c & ~long_c, false.copy()


def portfolio_kwargs(**params):
    return {}
