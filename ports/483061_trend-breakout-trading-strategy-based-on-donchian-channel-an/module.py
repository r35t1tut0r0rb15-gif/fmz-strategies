"""Donchian 20 expansions with the SMA 200 side, broker days: the 20-bar upper line rising over its own previous 20-bar high above the SMA 200 goes long, the lower line falling under its previous 20-bar low below the SMA 200 goes short; reversing.
Port of FMZ strategy #483061 "Trend Breakout Trading Strategy Based on Donchian Channel and Moving Average" (Donchian Channel Strategy with SMA 200 and Custom SL).

FMZ source id: 483061

Source
    https://www.fmz.com/strategy/483061 (PineScript v5, FMZ last modified 2025-02-27 17:07:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 145-184), Donchian 20; SMA 200; stops at 45 % of the mid-to-band distance; MPL 2.0 notice (ardhankurniawan)
    upper > highest(upper[1], 20) and close > sma200 -> entry Long;  lower < lowest(lower[1], 20) and close < sma200 -> entry Short
    every bar: exit Long (stop = mid - 0.45 (mid - lower));  exit Short (stop = mid + 0.45 (upper - mid))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are re-sent on every bar from the moving channel, so their levels follow the price: not
      ported, mark trailing_stop_pending (as the C185-C189 readings); the opposite entry is the exit. A
      repeat entry on the side held adds nothing, the other side reverses (REVERSAL INTENDED). No sizing
      code. The MPL 2.0 notice is kept with the verbatim copy (ported, stated). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the channel stops pending.
    2 generic: PASS, Donchian channel expansions with an SMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483061_donchian20_expansion_sma200_side_reversal"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "sma_length": [200, 100],
}
DEFAULT_PARAMS = {"length": 20, "sma_length": 200}


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
    n = int(p["length"])
    up, dn = h.rolling(n).max(), lo.rolling(n).min()
    ma = c.rolling(int(p["sma_length"])).mean()
    le = (up > up.shift(1).rolling(n).max()) & (c > ma)
    se = (dn < dn.shift(1).rolling(n).min()) & (c < ma)
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
