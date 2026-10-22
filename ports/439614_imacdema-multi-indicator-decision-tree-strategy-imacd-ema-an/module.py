"""Impulse MACD colours with the Ichimoku cloud, 30-minute bars: ohlc4 above both the zero-lag EMA 34 and the SMMA 34 of highs, with the EMA 40 above the cloud top 25 bars back, holds a long; ohlc4 not above
the zero-lag EMA and under the SMMA of lows, with the EMA 40 under the cloud bottom 25 bars back, holds a short; reversing.
Port of FMZ strategy #439614 "多指标决策树策略IMACDEMA和一目均衡表Multi-Indicator-Decision-Tree-Strategy-IMACD-EMA-and-Ichimoku" (Decision Tree Strategy: IMACD, EMA and Ichimoku [cryptoonchain]).

FMZ source id: 439614

Source
    https://www.fmz.com/strategy/439614 (PineScript v5, FMZ last modified 2024-01-22 11:25:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 128-190), IMACD 34 / signal 9; Ichimoku 9 / 26 / 52, displacement 26; EMA 40; bar colours off
    mdc = src > mi ? (src > hi ? lime : green) : (src < lo ? red : orange)  (src = ohlc4, hi / lo = smma(high / low, 34), mi = zlema(ohlc4, 34))
    a = max(leadLine1, leadLine2);  b = min(...);  lime and ema40 > a[25] -> entry Long;  red and ema40 < b[25] -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cloud values are taken 25 bars back (displacement - 1), past values only. The colour test
      compares the same rgb constant, so it is the src > hi branch. A same-side entry while in the
      position is ignored. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "30min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed averages and Ichimoku lines.
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

NAME = "fmz_439614_impulse_macd_colour_cloud_ema40"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [40, 20],
    "length_ma": [34, 21],
}
DEFAULT_PARAMS = {"ema_length": 40, "length_ma": 34, "conversion": 9, "base": 26, "span_b": 52, "displacement": 26}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + lo + c) / 4
    n = int(p["length_ma"])
    hi_s, lo_s = _rma(h, n), _rma(lo, n)
    e1 = src.ewm(span=n, adjust=False).mean()
    mi = 2 * e1 - e1.ewm(span=n, adjust=False).mean()

    def donch(k):
        return (lo.rolling(int(k)).min() + h.rolling(int(k)).max()) / 2

    l1 = (donch(p["conversion"]) + donch(p["base"])) / 2
    l2 = donch(p["span_b"])
    k = int(p["displacement"]) - 1
    top = pd.concat([l1, l2], axis=1).max(axis=1, skipna=False).shift(k)
    bot = pd.concat([l1, l2], axis=1).min(axis=1, skipna=False).shift(k)
    e40 = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    lime = (src > mi) & (src > hi_s)
    red = ~(src > mi) & (src < lo_s)
    false = pd.Series(False, index=c.index)
    return lime & (e40 > top), false, red & (e40 < bot), false.copy()


def portfolio_kwargs(**params):
    return {}
