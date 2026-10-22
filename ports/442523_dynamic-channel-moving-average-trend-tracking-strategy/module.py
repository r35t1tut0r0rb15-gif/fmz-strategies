"""Noro's price-channel bands, 1-hour bars: the trend is up after a close above the upper distance band with the low above the lower, down on the mirror; in an up trend a red bar closing under the upper
band goes long, in a down trend a green bar closing over the lower band goes short; reversing.
Port of FMZ strategy #442523 "Dynamic Channel Moving Average Trend Tracking Strategy" (Noro's Bands Strategy v1.0).

FMZ source id: 442523

Source
    https://www.fmz.com/strategy/442523 (PineScript v2, FMZ last modified 2024-02-22 15:51:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 144-193), period 20; long and short on; colour filter on; pyramiding 0; 100 % of equity
    center = (highest(close, 20) + lowest(close, 20)) / 2;  hd / ld = center +- sma(abs(close - center), 20)
    trend = close < ld and high < hd ? -1 : close > hd and low > ld ? 1 : trend[1]
    up = close < hd and trend == 1 and close < open -> entry Long;  dn = close > ld and trend == -1 and close > open -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both sides are enabled, so the entry quantity is the default. When both fire on one bar the later
      Short call wins (as #437773); they cannot, since the trend has one value. strategy.entry reverses:
      REVERSAL INTENDED. The 100 % of equity size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel distance bands with a trend state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND441138 (2 members, best partner #441138, Jaccard 0.697); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442523_noro_bands_trend_pullback_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "use_color": [True, False],
}
DEFAULT_PARAMS = {"length": 20, "use_color": True}


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
    center = (c.rolling(n).max() + c.rolling(n).min()) / 2
    dist = (c - center).abs().rolling(n).mean()
    hd, ld = center + dist, center - dist
    dn_t = ((c < ld) & (h < hd)).to_numpy()
    up_t = ((c > hd) & (lo > ld)).to_numpy()
    m = len(c)
    trend = np.zeros(m, dtype=np.int8)
    t = 0
    for i in range(m):
        if dn_t[i]:
            t = -1
        elif up_t[i]:
            t = 1
        trend[i] = t
    nocol = not p["use_color"]
    red = (c < o).to_numpy() | nocol
    green = (c > o).to_numpy() | nocol
    le = (c < hd).to_numpy() & (trend == 1) & red
    se = (c > ld).to_numpy() & (trend == -1) & green
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le & ~se, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
