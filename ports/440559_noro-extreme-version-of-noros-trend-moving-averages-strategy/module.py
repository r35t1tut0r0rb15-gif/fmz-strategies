"""Noro's price-channel trend, 1-hour bars: in an up trend (the low above the 21-bar channel centre for two bars) two red bars with the low under the 5-bar centre go long, the mirror in a down trend goes
short; the "extreme" rule also buys a red bar with the high under both centres; reversing.
Port of FMZ strategy #440559 "极端的Noro趋势均线策略Extreme-version-of-Noros-Trend-Moving-Averages-Strategy" (Trend MAs str 1.9 extreme).

FMZ source id: 440559

Source
    https://www.fmz.com/strategy/440559 (PineScript v2, FMZ last modified 2024-01-31 17:00:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-212), channel 21 / 5 on close; bars 2; fast filter on; extreme on; stops off
    center = (highest(close, 21) + lowest(close, 21)) / 2;  trend = low > center and low[1] > center[1] ? 1 : high < center and high[1] < center[1] ? -1 : trend[1]
    up = trend == 1 and low < center2 and two red bars;  dn = trend == -1 and high > center2 and two green bars;  up2 = high < center and high < center2 and red bar;  up or up2 -> entry Long;  dn -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop prices keep their previous (na) value with stops off, so the exit calls place nothing.
      dn2 is always 0 as written. The trend state starts na and only takes a value after the first
      qualifying bars. The short entry is written after the long one and wins on a bar with both (as
      #437773). strategy.entry reverses: REVERSAL INTENDED. The percent-of-equity size is sizing. FREQ
      = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price-channel centres and bar colours.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent of equity is sizing.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427506 (4 members, best partner #438058, Jaccard 0.779); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440559_noro_trend_channel_extreme"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slowlen": [21, 50],
    "fastlen": [5, 10],
}
DEFAULT_PARAMS = {"slowlen": 21, "fastlen": 5, "bars": 2, "needex": True}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    sl_, fl = int(p["slowlen"]), int(p["fastlen"])
    center = (c.rolling(sl_).max() + c.rolling(sl_).min()) / 2
    center2 = (c.rolling(fl).max() + c.rolling(fl).min()) / 2
    t_up = ((lo > center) & (lo.shift(1) > center.shift(1))).to_numpy()
    t_dn = ((h < center) & (h.shift(1) < center.shift(1))).to_numpy()
    trend = np.full(len(c), np.nan)
    tv = np.nan
    for i in range(len(c)):
        if t_up[i]:
            tv = 1.0
        elif t_dn[i]:
            tv = -1.0
        trend[i] = tv
    trend = pd.Series(trend, index=c.index)
    bar = pd.Series(np.where(c > o, 1, np.where(c < o, -1, 0)), index=c.index)
    nb = int(p["bars"])
    red = pd.Series(True, index=c.index)
    green = pd.Series(True, index=c.index)
    for k in range(nb):
        red &= bar.shift(k) == -1
        green &= bar.shift(k) == 1
    up = (trend == 1) & (lo < center2) & red
    dn = (trend == -1) & (h > center2) & green
    up2 = (h < center) & (h < center2) & (bar == -1)
    long_ = up | (up2 & bool(p["needex"]))
    false = pd.Series(False, index=c.index)
    return long_ & ~dn, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
