"""Hourly bars: the SMA 14 crossing over the SMA 21 with the close above both cloud lines of 26 bars ago and volume above its 20-bar average goes long; the mirror below the cloud goes short; reversing.
Port of FMZ strategy #439856 "基于SMA均线交叉配合市场深度指标一抛一的量化交易策略SMA-Crossover-Ichimoku-Market-Depth-Volume-Based-Quantitative-Trading-Strategy" (SMA Crossover with Ichimoku & Volume (SCIV)).

FMZ source id: 439856

Source
    https://www.fmz.com/strategy/439856 (PineScript v4, FMZ last modified 2024-01-24 14:21:42).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 156-193), SMA 14 / 21; volume SMA 20; Ichimoku 9 / 26 / 52, displacement 26
    buyEntry = crossover(sma14, sma21) and close > senkouA[26] and close > senkouB[26] and volume > sma(volume, 20) -> entry Buy
    sellEntry = crossunder(sma14, sma21) and close < senkouA[26] and close < senkouB[26] and volume > volumeMa -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cloud lines are read 26 bars back ([displacement]), i.e. the cloud drawn at the current bar.
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings filtered by the displaced Ichimoku cloud and volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439856_sma14_21_cross_ichimoku_cloud_volume_1h_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_sma": [14, 9],
    "long_sma": [21, 50],
}
DEFAULT_PARAMS = {"short_sma": 14, "long_sma": 21, "vol_len": 20, "tenkan": 9, "kijun": 26, "senkou_b": 52,
                  "displacement": 26}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    a = c.rolling(int(p["short_sma"])).mean()
    b = c.rolling(int(p["long_sma"])).mean()

    def mid(n):
        return (h.rolling(n).max() + lo.rolling(n).min()) / 2

    span_a = (mid(int(p["tenkan"])) + mid(int(p["kijun"]))) / 2
    span_b = mid(int(p["senkou_b"]))
    d = int(p["displacement"])
    sa, sb = span_a.shift(d), span_b.shift(d)
    vol_ok = v > v.rolling(int(p["vol_len"])).mean()
    co = (a > b) & (a.shift(1) <= b.shift(1))
    cu = (a < b) & (a.shift(1) >= b.shift(1))
    le = co & (c > sa) & (c > sb) & vol_ok
    se = cu & (c < sa) & (c < sb) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return le.astype(bool), false, se.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
