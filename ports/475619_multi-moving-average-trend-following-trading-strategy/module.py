"""SMA 50 / 100 crossings on the side of the SMA 200, daily bars: the cross up with the close at or over the SMA 200 goes long, the cross down at or under it goes short; any opposite cross closes the position; reversing.
Port of FMZ strategy #475619 "Multi Moving Average Trend Following Trading Strategy" (MA Cross Strategy).

FMZ source id: 475619

Source
    https://www.fmz.com/strategy/475619 (PineScript v6, FMZ last modified 2024-12-20 15:52:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-146), SMA 50 / 100 / 200
    crossover(sma50, sma100) and close >= sma200 -> entry Long;  crossunder and close <= sma200 -> entry Short;  crossunder and long -> close Long;  crossover and short -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close coinciding with the opposite entry only repeats the reversal (#437773), so it is masked
      on entry bars. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with an SMA 200 filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_475619_sma50_100_cross_sma200_side_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 20],
    "medium": [100, 50],
}
DEFAULT_PARAMS = {"fast": 50, "medium": 100, "slow": 200}


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
    f, md, s = (c.rolling(int(p[k])).mean() for k in ("fast", "medium", "slow"))
    up = (f > md) & (f.shift(1) <= md.shift(1))
    dn = (f < md) & (f.shift(1) >= md.shift(1))
    le = up & (c >= s)
    se = dn & (c <= s)
    return le, dn & ~se, se, up & ~le


def portfolio_kwargs(**params):
    return {}
