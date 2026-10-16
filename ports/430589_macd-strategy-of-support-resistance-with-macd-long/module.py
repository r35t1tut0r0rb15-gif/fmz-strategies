"""MACD 26 / 100 / 9 cross-up, broker days, long only: a MACD cross above its signal goes long with a 5 % stop and a 7.5 %
target from the signal close; the support filter is always true on historical bars.
Port of FMZ strategy #430589 "支撑阻力与MACD长线策略Strategy-of-Support-Resistance-with-MACD-LONG" (Price Action - Support & Resistance + MACD Strategy).

FMZ source id: 430589

Source
    https://www.fmz.com/strategy/430589 (PineScript v4, FMZ last modified 2023-10-30 16:18:34).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 155-191), MACD 26 / 100 / 9, stop 5 %, target 7.5 %
    supportPrice starts at 0 and only moves when low <= supportPrice or on barstate.islast
    bullishSetup = crossover(macd, signal) and hist > 0 and close > supportPrice -> entry long
    exit("Exit", "Long", stop = close x 0.95, limit = close x 1.075) on the signal bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * supportPrice stays 0 on every historical bar (low <= 0 never holds; barstate.islast is only the
      final bar), so "close > supportPrice" is always true: not ported (the last-bar branch is not
      reproducible on history).
    * The bracket is set on the signal bar and fixed as fractions of the fill (sl 0.05, tp 0.075). A
      later cross while long re-issues the exit with new levels in the source (a moved bracket):
      rule 2, mark trailing_stop_pending; the port keeps the entry's bracket.
    * Long only; Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). Stops
      on 1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry (re-issues on later signals approximated).
    2 generic: PASS, MACD and percentage exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430589_macd_26_100_bracket_long"
FAMILY = "macd_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "slow": [100, 50],
    "sl_pct": [5.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 26, "slow": 100, "signal": 9, "sl_pct": 5.0, "tp_pct": 7.5}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    long_e = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100, "tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
