"""Daily three-close breakouts with an SMA 10 cross, 1-hour bars: the close outside the last three completed days' close range, above the last day's low and crossing over its SMA 10 goes long; outside the
range, under the last completed week's high and crossing under the SMA 10 goes short; reversing.
Port of FMZ strategy #442526 "Dual Trendlines Breakout Golden Cross Death Cross Trend Following Strategy" (Support and resistant Strategy).

FMZ source id: 442526

Source
    https://www.fmz.com/strategy/442526 (PineScript v5, FMZ last modified 2024-02-22 16:01:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-185), no inputs; daily low, weekly high, daily highest / lowest close of 3 (request.security, no lookahead)
    breakout = close > security(D, highest(close, 3)) or close < security(D, lowest(close, 3))
    buy = breakout and close > security(D, low) and crossover(close, sma(close, 10)) -> entry Buy;  sell = breakout and close < security(W, high) and crossunder(close, sma10) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-5 request.security() without lookahead is read as the last completed higher bar (as
      #440503): the daily values are those of the last completed broker day, the weekly high that of
      the last completed broker week (Monday to Friday by broker-day label), built from the module's own
      bars. The 30-bar running low only plots (and never resets). strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily and weekly values from completed periods.
    2 generic: PASS, daily close-range breakouts with an SMA cross.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day and broker week (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442526_daily_close_range_break_sma10_cross_reversal"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "range_days": [3, 5],
    "sma_len": [10, 20],
}
DEFAULT_PARAMS = {"range_days": 3, "sma_len": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")   # the Monday of the broker week
    dc = c.groupby(day).last()
    k = int(p["range_days"])
    hh = pd.Series(dc.rolling(k).max().shift(1).reindex(day).to_numpy(), index=c.index)   # last completed days
    ll = pd.Series(dc.rolling(k).min().shift(1).reindex(day).to_numpy(), index=c.index)
    dlow = pd.Series(lo.groupby(day).min().shift(1).reindex(day).to_numpy(), index=c.index)
    whigh = pd.Series(h.groupby(week).max().shift(1).reindex(week).to_numpy(), index=c.index)   # last completed week
    brk = (c > hh) | (c < ll)
    s = c.rolling(int(p["sma_len"])).mean()
    up = (c > s) & (c.shift(1) <= s.shift(1))
    dn = (c < s) & (c.shift(1) >= s.shift(1))
    le = brk & (c > dlow) & up
    se = brk & (c < whigh) & dn
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
