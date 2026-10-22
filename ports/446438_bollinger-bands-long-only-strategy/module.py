"""Wide-band breakouts, daily bars, long only: the close crossing over the SMA 100 + 3 sd goes long; the close crossing under the SMA 100 - 1 sd closes.
Port of FMZ strategy #446438 "Bollinger Bands Long Only Strategy" (Bollinger Bands Long Only Strategy).

FMZ source id: 446438

Source
    https://www.fmz.com/strategy/446438 (PineScript v5, FMZ last modified 2024-03-28 16:36:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-133), SMA 100; upper 3 sd, lower 1 sd; margins 100 / 100
    crossover(close, basis + 3 sd) -> entry Long;  crossunder(close, basis - 1 sd) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's stdev is the population deviation. Long only. The margin settings are sizing. FREQ = "1D"
      from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, wide-band breakout with a lower-band exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the margin settings stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446438_sma100_3sd_break_1sd_exit_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult_upper": [3.0, 2.0],
    "mult_lower": [1.0, 2.0],
}
DEFAULT_PARAMS = {"mult_upper": 3.0, "mult_lower": 1.0, "length": 100}


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
    c = bars_df["close"]
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up = basis + float(p["mult_upper"]) * sd
    dn = basis - float(p["mult_lower"]) * sd
    c1 = c.shift(1)
    le = (c > up) & (c1 <= up.shift(1))
    lx = (c < dn) & (c1 >= dn.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
