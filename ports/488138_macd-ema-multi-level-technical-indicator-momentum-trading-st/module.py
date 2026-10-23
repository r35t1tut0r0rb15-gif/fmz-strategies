"""Hourly bars: the EMA 9 crossing over the EMA 26, or a MACD (9 / 26 / 9) cross-up on above-average volume, goes long; the mirrors go short; each signal closes the other side (always in the market after the first signal).
Port of FMZ strategy #488138 "多层次技术指标动量交易策略基于增强型MACD交易量强度和EMA信号系统-Multi-Level-Technical-Indicator-Momentum-Trading-Strategy-Based-on-Enhanced-MACD-Volume-Strength-and-EMA-Signal-System" (Enhanced MACD with Volume Strength and EMA Signals).

FMZ source id: 488138

Source
    https://www.fmz.com/strategy/488138 (PineScript v5, FMZ last modified 2025-03-25 14:04:00).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 150-195), EMA 9 / 26; MACD 9 / 26 / 9; volume / SMA 20 > 1
    buySignal = crossover(ema9, ema26) or (crossover(macd, signal) and volume / sma(volume, 20) > 1);  sellSignal mirrored
    entry Long when buySignal;  close Long when sellSignal;  entry Short when sellSignal;  close Short when buySignal

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each close repeats what the opposite entry already does (it reverses). On a bar with both a buy and
      a sell (an EMA cross-up with a MACD cross-down on volume, or the reverse), the later short entry
      wins, as written. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings or volume-confirmed MACD crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20 for the MACD branch; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488138_ema9_26_or_volume_macd_cross_1h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 12],
    "slow": [26, 34],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 26, "signal": 9, "vol_len": 20}


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
    c, v = bars_df["close"], bars_df["volume"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    macd = f - s
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    strong = v / v.rolling(int(p["vol_len"])).mean() > 1
    buy = ((f > s) & (f.shift(1) <= s.shift(1))) | ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & strong)
    sell = ((f < s) & (f.shift(1) >= s.shift(1))) | ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & strong)
    buy = buy & ~sell                        # the later short entry wins on a two-sided bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
