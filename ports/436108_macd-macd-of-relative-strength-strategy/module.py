"""MACD of relative strength, broker days, long only, with an 8 % stop: the close as a share of its 300-bar high, put through a MACD 14 / 26 / 10, buys when the histogram turns
positive (when not long) and closes when it turns negative; each long carries a stop 8 % under the signal close.
Port of FMZ strategy #436108 "相对强度MACD策略MACD-of-Relative-Strength-Strategy" (MACD OF RELATIVE STRENGHT STRATEGY).

FMZ source id: 436108

Source
    https://www.fmz.com/strategy/436108 (PineScript v5, FMZ last modified 2023-12-21 12:01:01).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 154-220), RS length 300; MACD 14 / 26 / 10; max risk 8 %
    rs = close / highest(high, 300);  hist of macd(rs, 14, 26, 10);  long and hist < 0 -> close;  hist > 0 and not long -> entry long, exit(stop = close (1 - 8 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is a fraction of the fill price: sl_stop 0.08, scalar (the author's level is the signal
      close). After a stop exit the entry is taken again on the next bar if the histogram is still positive,
      as the script does. The fixed-ratio quantity (money management) is sizing. The backtest period is
      the author's: dropped. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: REVIEW, relative-strength series and a percent stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed-ratio money management and cash order inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_436108_macd_of_relative_strength_long_stop"
FAMILY = "macd_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rs_length": [300, 150],
    "sl_max": [0.08, 0.05],
}
DEFAULT_PARAMS = {"rs_length": 300, "sl_max": 0.08, "fast": 14, "slow": 26, "signal": 10}


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
    h, c = bars_df["high"], bars_df["close"]
    rs = c / h.rolling(int(p["rs_length"])).max()
    macd = rs.ewm(span=int(p["fast"]), adjust=False).mean() - rs.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    le = (hist > 0).fillna(False).astype(bool)
    lx = (hist < 0).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_max"])}


def portfolio_kwargs(**params):
    return {}
