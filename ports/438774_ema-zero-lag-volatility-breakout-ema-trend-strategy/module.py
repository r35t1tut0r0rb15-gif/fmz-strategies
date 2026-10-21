"""Breakouts of the price / EMA 200 ratio above its upper Bollinger band, 10-minute bars: the ratio crossing over its 200-bar upper band (2 sigma) goes long while the EMA 200 rises, short while it falls;
reversing (binary mode: no other exit).
Port of FMZ strategy #438774 "即时突破波动率EMA趋势策略Zero-Lag-Volatility-Breakout-EMA-Trend-Strategy" (Zero-lag Volatility-Breakout EMA Trend Strategy).

FMZ source id: 438774

Source
    https://www.fmz.com/strategy/438774 (PineScript v5, FMZ last modified 2024-01-15 12:00:25).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 151-183), source close; EMA 200; band multiple 2; binary strategy on
    dif = max(close, ema 200) / min(close, ema 200) - 1;  [mid, upper, lower] = bb(dif, 200, 2);  crossover(dif, upper) and ema rising -> entry Long;  and ema falling -> entry Short
    not binary and crossunder(dif, mid) -> close Long, close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Binary mode is on, so positions end only at the opposite entry. stdev is the population deviation.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ratio to an EMA and its Bollinger band.
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

NAME = "fmz_438774_ema_ratio_band_breakout"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lx": [200, 100],
    "bbmult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"lx": 200, "bbmult": 2.0}


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
    c = bars_df["close"]
    n = int(p["lx"])
    ema = c.ewm(span=n, adjust=False).mean()
    dif = np.maximum(c, ema) / np.minimum(c, ema) - 1
    upper = dif.rolling(n).mean() + float(p["bbmult"]) * dif.rolling(n).std(ddof=0)
    x = (dif > upper) & (dif.shift(1) <= upper.shift(1))
    up = x & (ema > ema.shift(1))
    dn = x & (ema < ema.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
