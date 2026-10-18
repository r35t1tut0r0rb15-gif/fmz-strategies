"""EMA 13 / 48 crossings with an 8 % stop, broker days, long only: the EMA 13 crossing over the EMA 48 goes long; crossing under closes it; the
long also carries a stop at 1 / 1.08 of its average price. The short side is commented out in the script.
Port of FMZ strategy #435963 "Meticulous EMA Crossover Strategy" (EMA Strategy).

FMZ source id: 435963

Source
    https://www.fmz.com/strategy/435963 (PineScript v3, FMZ last modified 2023-12-20 14:28:36).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 184-221), EMA 13 / 48; initial stop at the average price / 1.08; the trailing-stop inputs are declared and unused
    goLong = crossover(fast, slow) -> entry "Buy";  killLong = crossunder(fast, slow) -> close "Buy";  exit("XLS", from_entry = "Buy", stop = avg / 1.08)   (the "Sell" side is commented out)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is a fraction of the fill price: sl_stop = 1 - 1/1.08 = 0.0741 (the "Initial Stop Loss
      Points" input is not used by the order). The trail inputs do nothing. Long only. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The 10 % of equity
      size and pyramiding 3 are sizing. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: REVIEW, trailing inputs unused; stop from the 1.08 divisor.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, pyramiding and trailing inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG435963 (2 members, best partner #439648, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_435963_ema_13_48_cross_long_stop"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [13, 8],
    "slow": [48, 34],
}
DEFAULT_PARAMS = {"fast": 13, "slow": 48, "divisor": 1.08}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = ((f > s) & (f.shift(1) <= s.shift(1))).fillna(False).astype(bool)
    lx = ((f < s) & (f.shift(1) >= s.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": 1.0 - 1.0 / float(p["divisor"])}


def portfolio_kwargs(**params):
    return {}
