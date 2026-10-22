"""Price-channel trend with pullback entries, 1-hour bars: in an uptrend (the low above the 20-bar close-channel midpoint) two red candles with the low under the EMA 5 go long; in a downtrend two green
candles with the high above the EMA 5 go short; reversing.
Port of FMZ strategy #440999 "Dual Moving Average Trend Tracking Strategy" (Trend MAs 1.5).

FMZ source id: 440999

Source
    https://www.fmz.com/strategy/440999 (PineScript v2, FMZ last modified 2024-02-04 15:57:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 130-195), long and short on; slow MA type 7 (price channel centre) of close, length 20; fast EMA 5 filter on; bars 2; 100 % of equity
    center = (highest(close, 20) + lowest(close, 20)) / 2;  trend = low > center ? 1 : high < center ? -1 : trend[1]
    up = trend == 1 and low < ema(close, 5) and two red bars -> entry Long;  dn = trend == -1 and high > ema5 and two green bars -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * MA type 7 is the price channel centre; the other types are not used. trend keeps its previous value
      between the two tests (na until the first). The entries are levels; an entry while already in that
      direction does nothing. strategy.entry reverses: REVERSAL INTENDED. The 100 % of equity size is
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel trend, EMA filter and candle colours.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427189 (2 members, best partner #427189, Jaccard 0.727); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440999_channel_trend_two_candle_pullback_reversal"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "bars": [2, 1],
}
DEFAULT_PARAMS = {"length": 20, "bars": 2, "fast_len": 5}


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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    center = ((c.rolling(n).max() + c.rolling(n).min()) / 2).to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    trend = np.full(m, np.nan)
    t = np.nan
    for i in range(m):
        if lv[i] > center[i]:
            t = 1.0
        elif hv[i] < center[i]:
            t = -1.0
        trend[i] = t
    fast = c.ewm(span=int(p["fast_len"]), adjust=False).mean()
    bar = np.sign(c - o)
    k = int(p["bars"])
    red = pd.Series(True, index=c.index)
    green = pd.Series(True, index=c.index)
    for j in range(k):
        red &= bar.shift(j) == -1
        green &= bar.shift(j) == 1
    tr = pd.Series(trend, index=c.index)
    le = (tr == 1) & (lo < fast) & red
    se = (tr == -1) & (h > fast) & green
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
