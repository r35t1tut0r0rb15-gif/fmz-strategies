"""Extreme-value volatility state, broker days: the 30-bar range-based volatility estimate over 0.005 goes long; under 0.0016 goes short; in between the earlier state holds; an optional switch trades the reverse.
Port of FMZ strategy #436598 "Statistical Volatility Backtest Strategy Based on Extreme Value Method" (Statistical Volatility - Extreme Value Method).

FMZ source id: 436598

Source
    https://www.fmz.com/strategy/436598 (PineScript v2, FMZ last modified 2023-12-26 10:24:53).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 160-184), length 30, top band 0.005, low band 0.0016, reverse off
    Vol = 0.5 (0.6 ln(highest(close) / lowest(close)) + 0.6 ln(highest(high) / lowest(low))) sqrt(253 / Length), clipped to [0, 2.99];  pos = 1 if Vol > top, -1 if Vol < low, else pos[1]
    possig = -pos when reverse;  possig == 1 -> entry Long;  possig == -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is a level, so the entry is sent on every bar of the state; a same-side entry while in
      the position is ignored (pyramiding 0). The volatility estimate is above 0.005 on almost any
      instrument, so the long state dominates. REVERSAL INTENDED. The default quantity is sizing.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volatility estimate state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436598_extreme_value_volatility_state"
FAMILY = "volatility_regime"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [30, 60],
    "top_band": [0.005, 0.01],
}
DEFAULT_PARAMS = {"length": 30, "top_band": 0.005, "low_band": 0.0016, "reverse": False}


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
    sq = np.sqrt(253.0 / n)
    with np.errstate(divide="ignore", invalid="ignore"):
        vol = (0.6 * np.log(c.rolling(n).max() / c.rolling(n).min()) * sq
               + 0.6 * np.log(h.rolling(n).max() / lo.rolling(n).min()) * sq) * 0.5
    nres = vol.clip(lower=0.0, upper=2.99).to_numpy()
    top, low = float(p["top_band"]), float(p["low_band"])
    m = len(nres)
    pos = np.zeros(m)
    prev = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if nres[i] > top:
                prev = 1.0
            elif nres[i] < low:
                prev = -1.0
            pos[i] = prev
    sig = -pos if p["reverse"] else pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(sig == 1, index=ix), false, pd.Series(sig == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
