"""Pullbacks against an EMA 50 / 200 trend with three confirmations, bar size pending: in an up trend (EMA 50 above EMA 200),
RSI 14 under 30 with the close under the lower Bollinger band and the MACD above its signal goes long; the mirror
(down trend, RSI over 70, close over the upper band, MACD under its signal) goes short; each signal also closes the
other side.
Port of FMZ strategy #434970 "Momentum Reversal Trend Tracking Strategy" (Forex and Crypto Trading Strategy).

FMZ source id: 434970

Source
    https://www.fmz.com/strategy/434970 (PineScript v5, FMZ last modified 2023-12-11 13:45:55).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 121-162), EMA 50 / 200; RSI 14, 30 / 70; BB 20 / 2; MACD 12 / 26 / 9; no backtest header
    buy = ema50 > ema200 and rsi < 30 and close < bb_lower and macd > signal -> entry long, close short
    sell = ema50 < ema200 and rsi > 70 and close > bb_upper and macd < signal -> entry short, close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1).
      precompute builds the bars with the house bar_sizes.build_bars(raw_1m_df, params["bar_size"]);
      the driver supplies bar_size (never in GRID / DEFAULT_PARAMS).
    * Wilder RSI, population stdev, EMA MACD. strategy.entry reverses: REVERSAL INTENDED.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, averages, RSI, bands and MACD.
    3 crypto-exchange-only: no.
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_434970_trend_pullback_rsi_bb_macd"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size: the driver supplies params["bar_size"]
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_lvl": [30, 40],
    "fast": [50, 20],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200, "rsi_len": 14, "rsi_lvl": 30, "bb_len": 20, "bb_mult": 2.0}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())
    b = int(p["bb_len"])
    mid, sd = c.rolling(b).mean(), c.rolling(b).std(ddof=0)
    bu, bl = mid + float(p["bb_mult"]) * sd, mid - float(p["bb_mult"]) * sd
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    lv = float(p["rsi_lvl"])
    le = ((ef > es) & (rsi < lv) & (c < bl) & (macd > sig)).astype(bool)
    se = ((ef < es) & (rsi > 100 - lv) & (c > bu) & (macd < sig)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
