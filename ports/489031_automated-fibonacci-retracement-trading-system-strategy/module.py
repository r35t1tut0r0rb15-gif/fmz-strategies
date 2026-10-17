"""Fibonacci 61.8 % / 38.2 % crosses of the 20-bar swing with a 1 % / 2 % bracket, broker days: the close crossing above
the 61.8 % level of the 20-bar range goes long; crossing below the 38.2 % level goes short; each trade has a 1 % stop
and a 2 % target.
Port of FMZ strategy #489031 "自动化斐波那契回撤交易系统策略-Automated-Fibonacci-Retracement-Trading-System-Strategy" (Estrategia Fibonacci con Señales).

FMZ source id: 489031

Source
    https://www.fmz.com/strategy/489031 (PineScript v5, FMZ last modified 2025-04-01 13:25:30).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 164-195), swing 20, levels 0.382 / 0.618, SL 1 %, TP 2 %
    fib618 = low20 + 0.618 x range;  fib382 = low20 + 0.382 x range   (range = highest(high, 20) - lowest(low, 20))
    crossover(close, fib618) -> entry long + exit(stop = close x 0.99, limit = close x 1.02);  crossunder(close, fib382) -> short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The swing window includes the current bar. The bracket is placed once, on the signal bar: sl_stop 1 %, tp_stop
      2 % of the fill (scalars, house rule). The risk-based quantity is sizing.
    * Entries reverse (REVERSAL INTENDED); the two crosses cannot fall on one bar.
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, range fractions and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 1 %-risk quantity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_489031_fib_618_382_cross_bracket"
FAMILY = "pivot_levels"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [20, 50],
    "sl_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"lookback": 20, "sl_pct": 1.0, "tp_pct": 2.0}


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
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["lookback"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    f618, f382 = ll + (hh - ll) * 0.618, ll + (hh - ll) * 0.382
    long_e = ((c > f618) & (c.shift(1) <= f618.shift(1))).astype(bool)
    short_e = ((c < f382) & (c.shift(1) >= f382.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
