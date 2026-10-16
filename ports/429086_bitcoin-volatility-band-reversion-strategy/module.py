"""Volatility-band reversion, 4-hour bars: a bar's percentage change between the inner and outer lower bands
of its own 7-bar distribution, in an SMA 50 up-trend and above the 7-bar lowest close, goes long; the mirror
goes short (the source's conditional bracket is described, not emitted).
Port of FMZ strategy #429086 "Bitcoin Volatility Band Reversion Strategy" (BTC Volatility Band Strategy).

FMZ source id: 429086

Source
    https://www.fmz.com/strategy/429086 (PineScript v4, FMZ last modified 2023-10-12 17:38:39).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 176-249), MA 7, inner 1, outer 2 deviations; SMA 50 of close[1]; risk = range of the bar 7 back / 7
    chg = (close - close[1]) / close x 100; mid = sma(chg,7); lower1 / lower2 = mid - 1 / 2 stdev(chg,7)
    long: lower2 < chg <= lower1 and close[1] > sma(close[1],50) and close > lowest(close,7) -> entry long
    short: upper1 <= chg < upper2 and close[1] < sma(close[1],50) and close < highest(close,7) -> entry short
    on a signal bar: exit(stop = avg -/+ 0.65 risk, limit = avg +/- 1.15 risk), risk = (high[7] - low[7]) / 7

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed only on a bar that signals, from strategy.position_avg_price at that bar's
      close: on the entry bar the position is still flat (na price: no bracket); a later signal bar in
      the same direction places one, sized from that bar's risk and re-placed on each such bar. A stop
      set after entry and moved later cannot be expressed by stops() (rule 2): not emitted; mark
      trailing_stop_pending, described in PORT_NOTES.
    * stdev is the population deviation. The date window is dropped (2000-2100).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the conditional bracket is not emitted (rule 2).
    2 generic: PASS, percentage changes, moving averages and bar ranges.
    3 crypto-exchange-only: no ("Bitcoin" in the name only; exchange pair in the header).
    4 signals only: no sizing code; the bracket is quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_429086_volatility_band_reversion"
FAMILY = "mean_reversion_band"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [7, 14],
    "inner": [1.0, 1.5],
}
DEFAULT_PARAMS = {"ma_len": 7, "inner": 1.0, "outer": 2.0, "trend": 50, "price_len": 7}


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
    chg = (c - c.shift(1)) / c * 100
    n = int(p["ma_len"])
    mid, sd = chg.rolling(n).mean(), chg.rolling(n).std(ddof=0)
    lower1, lower2 = mid - p["inner"] * sd, mid - p["outer"] * sd
    upper1, upper2 = mid + p["inner"] * sd, mid + p["outer"] * sd
    c1 = c.shift(1)
    t = c1.rolling(int(p["trend"])).mean()
    k = int(p["price_len"])
    long_e = ((chg <= lower1) & (chg > lower2) & (c1 > t) & (c > c.rolling(k).min())).astype(bool)
    short_e = ((chg >= upper1) & (chg < upper2) & (c1 < t) & (c < c.rolling(k).max())).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
