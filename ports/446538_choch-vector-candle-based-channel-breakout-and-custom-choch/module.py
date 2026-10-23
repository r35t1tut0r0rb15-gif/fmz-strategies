"""Hourly bars, long only: two or more of the last 3 bars being down "vector candles" (volume above twice its 10-bar average) goes long; two or more up vector candles in the last 3 bars closes it.
Port of FMZ strategy #446538 "基于向量蜡烛图的通道突破与自定义ChoCH策略-Vector-Candle-based-Channel-Breakout-and-Custom-ChoCH-Strategy" (Custom ChoCH and BOS Strategy with Vector Candles).

FMZ source id: 446538

Source
    https://www.fmz.com/strategy/446538 (PineScript v4, FMZ last modified 2024-03-29 14:45:57).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 102-135), volume SMA 10; multiplier 2; confirmation candles 3
    vectorCandleRed = close < open and volume > sma(volume, 10) x 2;  buyCondition = sum(vectorCandleRed, 3) >= 2 -> entry Buy
    vectorCandleGreen = close > open and volume > avgVol x 2;  sellCondition = sum(vectorCandleGreen, 3) >= 2 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ChoCH / BOS shapes and the blue / purple candles only plot. Buying after heavy-volume down
      candles is contrarian, as written. The entry is called before the close: from flat a bar with both
      conditions enters; while long it closes. Long only. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, clusters of heavy-volume candles.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against twice its SMA 10; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446538_heavy_volume_down_candle_cluster_1h_long_only"
FAMILY = "volume_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vol_mult": [2.0, 1.5],
    "length": [10, 20],
}
DEFAULT_PARAMS = {"length": 10, "vol_mult": 2.0, "confirm": 3}


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
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    heavy = v > v.rolling(int(p["length"])).mean() * float(p["vol_mult"])
    red = ((c < o) & heavy).astype(float)
    green = ((c > o) & heavy).astype(float)
    k = int(p["confirm"])
    buy = (red.rolling(k).sum() >= 2).to_numpy()
    sell = (green.rolling(k).sum() >= 2).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and sell[i]:
            lx[i], pos = True, 0
        elif pos == 0 and buy[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
