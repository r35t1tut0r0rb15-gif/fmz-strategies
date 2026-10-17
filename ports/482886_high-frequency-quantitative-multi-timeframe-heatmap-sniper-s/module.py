"""Close crossing a smoothed 50-bar low (high) "heatmap" band in the SMA 50 / 200 trend, always in the market,
1-hour bars: with SMA 50 above SMA 200, the close crossing above SMA(lowest low 50, 50) goes long; with SMA 50 at or
below SMA 200, the close crossing below SMA(highest high 50, 50) goes short.
Port of FMZ strategy #482886 "高频量化多周期热图狙击策略-High-Frequency-Quantitative-Multi-Timeframe-Heatmap-Sniper-Strategy" (Ultimate Heatmap Sniper Bot).

FMZ source id: 482886

Source
    https://www.fmz.com/strategy/482886 (PineScript v6, FMZ last modified 2025-02-20 16:35:47).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 109-138), sensitivity 50, week MA 50, month MA 200, lookback 50
    heatmapLow = sma(lowest(low, 50), 50); heatmapHigh = sma(highest(high, 50), 50); trend = sma50 > sma200 ? 1 : -1
    long = crossover(close, heatmapLow) and trend == 1; short = crossunder(close, heatmapHigh) and trend == -1

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "week" / "month" MAs are 50 / 200 bars of the chart, as written; "Max Trades Per Day" is never used.
    * Entries reverse (REVERSAL INTENDED); no exits, no stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed rolling extremes and moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_482886_heatmap_band_cross_trend_reversal"
FAMILY = "channel_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sensitivity": [50, 20],
    "lookback": [50, 20],
}
DEFAULT_PARAMS = {"sensitivity": 50, "week_ma": 50, "month_ma": 200, "lookback": 50}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    lb, sens = int(p["lookback"]), int(p["sensitivity"])
    hm_lo = lo.rolling(lb).min().rolling(sens).mean()
    hm_hi = h.rolling(lb).max().rolling(sens).mean()
    up = c.rolling(int(p["week_ma"])).mean() > c.rolling(int(p["month_ma"])).mean()
    long_e = ((c > hm_lo) & (c.shift(1) <= hm_lo.shift(1)) & up).astype(bool)
    short_e = ((c < hm_hi) & (c.shift(1) >= hm_hi.shift(1)) & ~up).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
