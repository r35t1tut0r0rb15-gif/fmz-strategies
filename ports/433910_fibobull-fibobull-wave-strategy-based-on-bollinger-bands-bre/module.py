"""Bollinger breakout regime flips, broker days: with a 21-bar, 1-sd band, the regime turns long when the latest close above
the upper band is more recent than the latest close below the lower band, and short in the mirror case; each flip
reverses the position.
Port of FMZ strategy #433910 "基于布林带突破的FiboBuLL波浪策略FiboBuLL-Wave-Strategy-Based-on-Bollinger-Bands-Breakout" (FiboBuLL Wave (Bollinger Bands Breakout)).

FMZ source id: 433910

Source
    https://www.fmz.com/strategy/433910 (PineScript v5, FMZ last modified 2023-12-01 14:11:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 191-262), SMA 21, stdev 1.0, trade type Both
    long = close > upper;  short = close < lower;  L1 = barssince(long), S1 = barssince(short)
    longSignal = L1 < S1 and not (L1 < S1)[1] -> entry long;  shortSignal = S1 < L1 and not (S1 < L1)[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close of 'LongAL' names no open entry (the long is 'AL'), so only the opposite entry ends a
      long, as written. Pine's stdev is the population stdev; barssince is undefined until the first
      break (no signal before it).
    * strategy.entry reverses: REVERSAL INTENDED. The date window is open from 2018. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band breaks and their recency.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG433910 (2 members, best partner #438821, Jaccard 0.974); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433910_fibobull_band_regime"
FAMILY = "bollinger_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 42],
    "mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 21, "mult": 1.0}


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


def _barssince(v):
    out = np.full(len(v), np.nan)
    last = -1
    for i in range(len(v)):
        if v[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    l1 = _barssince((c > basis + dev).to_numpy())
    s1 = _barssince((c < basis - dev).to_numpy())
    with np.errstate(invalid="ignore"):
        lt = l1 < s1
        st = s1 < l1
    lt1 = np.concatenate(([False], lt[:-1]))
    st1 = np.concatenate(([False], st[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(lt & ~lt1, index=ix), false, pd.Series(st & ~st1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
