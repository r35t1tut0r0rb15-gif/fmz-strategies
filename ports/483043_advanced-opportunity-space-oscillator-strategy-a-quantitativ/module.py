"""Hourly bars: a bullish fair-value gap (low above the high of two bars earlier) confirmed by above-average volume on the previous bar or a gap over 1.5 x its 50-bar average goes long; the mirrored bearish gap goes short; the opposite signal reverses.
Port of FMZ strategy #483043 "Advanced Opportunity Space Oscillator Strategy A Quantitative Trading System Based on Fair Value Gaps" (FVG Oscillator Strategy (OmegaTools)).

FMZ source id: 483043

Source
    https://www.fmz.com/strategy/483043 (PineScript v5, FMZ last modified 2025-02-24 14:55:25).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 106-204), bfvg = low > high[2]; sfvg = high < low[2]; volume SMA 10 (previous bar); gap > 1.5 x its SMA 50; 100 % of equity
    verifyb = (bfvg and vol[1]) or (bfvg and (low - high[2]) > sma(low - high[2], 50) x 1.5) -> close Short FVG, entry Long FVG
    verifys = (sfvg and vol[1]) or (sfvg and (high - low[2]) > sma(high - low[2], 50) x 1.5) -> close Long FVG, entry Short FVG

Interpretation choices (Pine rules in SURVEY_README.md)
    * vol[1] is the previous bar's volume test (volume > its SMA 10). The gap-size test for shorts
      compares high - low[2] (negative on a bearish gap) with 1.5 x its average, as written. The closes
      only repeat what the opposite entry already does (it reverses). The oscillator counts and plots
      feed nothing. REVERSAL INTENDED. 100 % of equity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, fair-value gaps confirmed by volume or gap size.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 10 on the previous bar; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483043_fvg_gap_volume_or_size_confirmed_1h_reversal"
FAMILY = "gap"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lnt": [50, 100],
    "size_mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"lnt": 50, "size_mult": 1.5}


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
    h, lo, v = bars_df["high"], bars_df["low"], bars_df["volume"]
    n, k = int(p["lnt"]), float(p["size_mult"])
    vol_prev = (v > v.rolling(10).mean()).shift(1, fill_value=False)
    bgap, sgap = lo - h.shift(2), h - lo.shift(2)
    bfvg, sfvg = lo > h.shift(2), h < lo.shift(2)
    buy = bfvg & (vol_prev | (bgap > bgap.rolling(n).mean() * k))
    sell = sfvg & (vol_prev | (sgap > sgap.rolling(n).mean() * k))   # a bullish and a bearish gap never meet
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
