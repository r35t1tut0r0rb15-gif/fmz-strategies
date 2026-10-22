"""Vix Fix spike endings, 1-hour bars, long only: a green bar on which the Williams Vix Fix (22) drops back under both its Bollinger band (20, 2) and 85 % of its 50-bar high, after being above either,
goes long from flat; any red bar closes.
Port of FMZ strategy #440507 "基于renko股票日内低点回撤的stock日内交易策略Intraday-Trading-Strategy-for-Stocks-Based-on-Renko-Low-Point-Retracement" (Renko Stock Daily).

FMZ source id: 440507

Source
    https://www.fmz.com/strategy/440507 (PineScript v2, FMZ last modified 2024-01-31 10:53:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-158), highest close 22; BB 20 / 2; 50-bar high x 0.85
    Situacion = (highest(close, 22) - low) / highest(close, 22) x 100;  bands = sma 20 + 2 sd, 0.85 x highest 50
    (prev above either band) and (now under both) and close > open and position <= 0 -> entry Entrar;  close < open -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Despite the name the script runs on the chart's own bars (no Renko). The entry and close tests
      cannot hold together. Pine's stdev is the population deviation. Long only. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Vix Fix and its bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440507_vix_fix_spike_end_long"
FAMILY = "volatility_spike_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pd": [22, 14],
    "ph": [0.85, 0.9],
}
DEFAULT_PARAMS = {"pd": 22, "ph": 0.85, "bbl": 20, "mult": 2.0, "lb": 50}


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
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    hc = c.rolling(int(p["pd"])).max()
    s = (hc - lo) / hc * 100
    bbl = int(p["bbl"])
    r11 = s.rolling(bbl).mean() + float(p["mult"]) * s.rolling(bbl).std(ddof=0)
    r22 = s.rolling(int(p["lb"])).max() * float(p["ph"])
    was = (s.shift(1) >= r11.shift(1)) | (s.shift(1) >= r22.shift(1))
    now_in = (s < r11) & (s < r22)
    buy = was & now_in & (c > o)
    sell = c < o
    false = pd.Series(False, index=c.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
