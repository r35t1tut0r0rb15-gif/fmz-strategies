"""The close crossing the SMA 50 of the 50-bar low / high with the SMA 50 / 200 trend, hourly bars: up through the smoothed low with SMA 50 over SMA 200 goes long, down through the smoothed high with SMA 50 under SMA 200 goes short; reversing, no other exit.
Port of FMZ strategy #482886 "High Frequency Quantitative Multi Timeframe Heatmap Sniper Strategy" (Ultimate Heatmap Sniper Bot).

FMZ source id: 482886

Source
    https://www.fmz.com/strategy/482886 (PineScript v6, FMZ last modified 2025-02-20 16:35:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 105-162), lookback 50; sensitivity 50; SMA 50 / 200; max trades per day 6 (unused); 1 % of equity
    heatmapLow = sma(lowest(low, 50), 50);  heatmapHigh = sma(highest(high, 50), 50);  trend = sma50 > sma200 ? 1 : -1
    crossover(close, heatmapLow) and trend == 1 -> entry Sniper Long;  crossunder(close, heatmapHigh) and trend == -1 -> entry Sniper Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The warnings, reversal diamonds and projection are drawing only; "Max Trades Per Day" feeds nothing.
      Entries only: each reverses the other side (REVERSAL INTENDED), no other exit. The 1 % of equity
      size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed channel crossings with an SMA trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1 % of equity stored, not ported.
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

NAME = "fmz_482886_smoothed_50bar_low_high_cross_sma50_200_trend_reversal"
FAMILY = "mean_reversion_band"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [50, 100],
    "sensitivity": [50, 20],
}
DEFAULT_PARAMS = {"lookback": 50, "sensitivity": 50, "week_ma": 50, "month_ma": 200}


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
    n, s = int(p["lookback"]), int(p["sensitivity"])
    hl = lo.rolling(n).min().rolling(s).mean()
    hh = h.rolling(n).max().rolling(s).mean()
    up = c.rolling(int(p["week_ma"])).mean() > c.rolling(int(p["month_ma"])).mean()
    le = (c > hl) & (c.shift(1) <= hl.shift(1)) & up
    se = (c < hh) & (c.shift(1) >= hh.shift(1)) & ~up
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
