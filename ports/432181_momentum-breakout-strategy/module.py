"""Rising 18-bar momentum, broker days: the 18-bar momentum above zero and still rising goes long, below zero and still
falling goes short; fixed 8 % (long) and 7 % (short) stops from the fill. A stopped trade re-enters on the next bar
whose momentum still agrees, as written.
Port of FMZ strategy #432181 "Momentum Breakout Strategy" (Momentum BF).

FMZ source id: 432181

Source
    https://www.fmz.com/strategy/432181 (PineScript v4, FMZ last modified 2023-11-15 11:09:21).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 199-285), momentum 18, fixed stops 8 % long / 7 % short (type "Fixed")
    mom0 = close - close[18];  mom1 = mom0 - mom0[1]
    mom0 > 0 and mom1 > 0 -> entry long;  mom0 < 0 and mom1 < 0 -> entry short
    exit(stop = avg price x (1 - 8 %), when = bars since entry > 0);  short: avg price x (1 + 7 %)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are fixed fractions of the fill price by side (the default type "Fixed"; the "ATR
      Derived" option is an input not used). Pine places them from the bar after the signal bar
      (since_longEntry > 0), so they are live from the fill bar's close; the house stop is live on the
      fill bar too (stated).
    * strategy.entry fires on every bar the momentum agrees: after a stop the next such bar re-enters,
      and an opposite signal reverses: REVERSAL INTENDED. useLongs / useShorts are both true, so the
      close branches are inert. The test-period inputs are not used (testPeriod() is always true).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; stops on
      daily bars: mark coarse_bar_stop. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stops fixed at entry.
    2 generic: PASS, momentum signs and percentage stops of the fill.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the commission stored in original_sizing.txt.
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

NAME = "fmz_432181_momentum_rising_pct_stop"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [18, 9],
    "sl_scale": [1.0, 0.5],
}
DEFAULT_PARAMS = {"length": 18, "sl_long": 8.0, "sl_short": 7.0, "sl_scale": 1.0}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    m0 = c - c.shift(int(p["length"]))
    m1 = m0 - m0.shift(1)
    le = ((m0 > 0) & (m1 > 0)).astype(bool)
    se = ((m0 < 0) & (m1 < 0)).astype(bool)
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    k = float(p["sl_scale"]) / 100
    sl = pd.Series(np.nan, index=bars_df.index)
    sl[le] = float(p["sl_long"]) * k
    sl[se] = float(p["sl_short"]) * k
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
