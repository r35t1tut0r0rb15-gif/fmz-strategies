"""Three Line Strike candles, broker days: three red candles followed by a larger green one goes long, three green followed by a larger red one goes short; reversing, no other exit.
Port of FMZ strategy #483050 "基于多重K线形态的三重打击量化交易策略-Multi-Candlestick-Pattern-Based-Triple-Strike-Quantitative-Trading-Strategy" (3 Line Strike [TTF] - Strategy).

FMZ source id: 483050

Source
    https://www.fmz.com/strategy/483050 (PineScript v5, FMZ last modified 2025-02-27 17:12:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-257), 3 Line Strike on (both); big-candle engulfing entries off by default; pyramiding 0; 100 % of equity, capital 100000
    red [1..3] and green candle with a larger body than the last -> entry 3LS_Bull;  green [1..3] and larger red -> entry 3LS_Bear
    (big-candle engulfing entries: off by default)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The engulfing-candle entries are switched off by default (showBullEngulfing / showBearEngulfing
      false), so they are not ported; the alerts and plots are drawing only. "Larger" compares the
      bodies' absolute sizes. Entries only: each reverses the other side (REVERSAL INTENDED), no other
      exit. No numeric input reaches the orders (GRID {}). The 100 % of equity size and the capital are
      sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, three-line-strike candles.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483050_three_line_strike_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    o, c = bars_df["open"], bars_df["close"]
    col = np.sign(c - o)
    larger = (c - o).abs() > (c.shift(1) - o.shift(1)).abs()
    bull = (col.shift(1) < 0) & (col.shift(2) < 0) & (col.shift(3) < 0) & larger & (col > 0)
    bear = (col.shift(1) > 0) & (col.shift(2) > 0) & (col.shift(3) > 0) & larger & (col < 0)
    false = pd.Series(False, index=c.index)
    return bull & ~bear, false, bear, false.copy()


def portfolio_kwargs(**params):
    return {}
