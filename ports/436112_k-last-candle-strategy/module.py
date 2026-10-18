"""Follow yesterday's candle, broker days, with a bracket: a green previous day goes long, a red one goes short (reversing, and again after any bracket exit);
each trade carries a stop and a target taken from tick amounts re-expressed as fractions of the price.
Port of FMZ strategy #436112 "最后K线趋势跟踪策略Last-Candle-Strategy" (Last Candle Strategy with Date Range).

FMZ source id: 436112

Source
    https://www.fmz.com/strategy/436112 (PineScript v5, FMZ last modified 2023-12-21 12:15:23).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 134-158), previous daily open and close (lookahead_on with [1]); stop = 1 % of the open, target = the close, both in ticks
    tradeDirection = previous day close > previous day open ? 1 : -1;  entry "Buy" (1) / "Sell" (-1) on every bar;  exit(loss = 0.01 open, profit = close)   (loss and profit are in TICKS)

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security(..., "D", open[1], lookahead_on) with the [1] is the previous completed day (no
      look-ahead): here the previous bar of the daily chart. The conditions are states re-sent every bar,
      so a position is re-opened on the bar after a bracket exit. Criterion 2: loss and profit are passed in
      TICKS, so 0.01 x open and the close become price distances of 0.01 x open x mintick and close x
      mintick: the port reads them as fractions of the price with a 0.1 tick (sl_frac 0.001, tp_frac 0.1;
      0.01 and 0.02 as a plausible alternative). The date range is the author's: dropped.
      Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. REVERSAL
      INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick amounts -> fractions of the price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick inputs quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_436112_follow_last_day_bracket"
FAMILY = "momentum_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_frac": [0.001, 0.01],
    "tp_frac": [0.1, 0.02],
}
DEFAULT_PARAMS = {"sl_frac": 0.001, "tp_frac": 0.1}


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
    last_open, last_close = o.shift(1), c.shift(1)
    known = last_open.notna() & last_close.notna()
    le = ((last_open < last_close) & known).astype(bool)
    se = (~(last_open < last_close) & known).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
