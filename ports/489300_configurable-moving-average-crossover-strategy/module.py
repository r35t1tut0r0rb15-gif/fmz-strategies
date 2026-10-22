"""Close crossings over the EMA 13 with the EMA 13 over the EMA 55 and the close over the EMA 34, 2-day bars, long only: the cross goes long, a close under the EMA 34 closes.
Port of FMZ strategy #489300 "Configurable Moving Average Crossover Strategy" (Configurable MA Cross (MA-X) Strategy).

FMZ source id: 489300

Source
    https://www.fmz.com/strategy/489300 (PineScript v6, FMZ last modified 2025-04-03 11:31:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 125-202), EMA 13 / 55 / 34 (type EMA); shorts off; exit after 2+ bars; 10 % of equity, commission 0.06 %
    crossover(close, ema13) and ema13 > ema55 and close > ema34 -> entry Long, counter := 1;  long and counter >= 2 and close < ema34 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bar counter reaches 2 on the fill bar and is reset to 1 only on an entry bar, whose close is over
      the EMA 34, so it never blocks the exit. Shorts are off by default. Long only. MPL 2.0 source (the
      notice is kept: Mozilla Public License 2.0, © YetAnotherTA). Bars are blocks of two broker days
      (17:00 America/New_York) counted from 1970-01-01, stamped with their first minute. FREQ = "2D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA breakouts in an EMA stack with an EMA exit.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity and commission stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489300_close_ema13_cross_ema55_stack_ema34_exit_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "maPeriodA": [13, 8],
    "maPeriodC": [34, 21],
}
DEFAULT_PARAMS = {"maPeriodA": 13, "maPeriodC": 34, "maPeriodB": 55, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    a, b, x = ema(p["maPeriodA"]), ema(p["maPeriodB"]), ema(p["maPeriodC"])
    le = (c > a) & (c.shift(1) <= a.shift(1)) & (a > b) & (c > x)
    lx = (c < x) & ~le
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
