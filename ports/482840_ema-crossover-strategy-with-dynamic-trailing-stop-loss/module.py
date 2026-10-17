"""Close crosses of the EMA 68, always in, two-day bars: a close crossing above the EMA goes long, below goes short.
Port of FMZ strategy #482840 "指数移动平均线交叉结合动态止损策略-EMA-Crossover-Strategy-with-Dynamic-Trailing-Stop-Loss" (EMA 68 with Trailing Stop-Loss).

FMZ source id: 482840

Source
    https://www.fmz.com/strategy/482840 (PineScript v5, FMZ last modified 2025-02-20 14:17:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 105-146), EMA 68, stop 20 points, trail adjustment 10 points
    crossover(close, ema68) -> entry long, is_long; crossunder -> entry short, is_short
    while is_long: exit(stop = entry - 20 (entry + 10 after a close at entry + 20), when = close < ema68)
    (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits never act: `when = close < ema68` is first true on the crossunder bar, where the short entry written
      before it has already cleared is_long (the short mirrored), so no stop is ever placed. Dropped as inert (as
      #492009); the 20 / 10-point distances (0.02 % of a BTC_USDT price) would be inert on the author's market too.
    * Every cross is an entry signal; entries reverse (REVERSAL INTENDED), so the strategy is always in after the
      first cross. Signal module, no stops. Two-day bars are blocks of broker-day dates from 1970-01-01 (decision
      owed, as #426509); FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, one EMA (the point stops are inert and dropped).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in two-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482840_ema68_close_cross_always_in_2d"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [68, 34],
}
DEFAULT_PARAMS = {"ema_len": 68}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=2):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    long_e = ((c > ema) & (c.shift(1) <= ema.shift(1))).astype(bool)
    short_e = ((c < ema) & (c.shift(1) >= ema.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
