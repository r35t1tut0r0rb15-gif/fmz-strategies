"""Indicator integrator, broker days: the sum of the last 19 values of close minus its SMA 170 above zero holds a long,
below zero holds a short.
Port of FMZ strategy #431249 "Momentum Integral Indicator Strategy" (Indicator Integrator Strat).

FMZ source id: 431249

Source
    https://www.fmz.com/strategy/431249 (PineScript v2, FMZ last modified 2023-11-06 14:40:26).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 226-261), SMA 170, summation 18 (19 terms)
    k = close - sma(close, 170); sum = k[0] + k[1] + ... + k[18]  (for i = 0 to 18)
    sum > 0 -> entry long (else cancel);  sum < 0 -> entry short (else cancel)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "for i = 0 to s" adds s + 1 = 19 terms, as written. The cancels only withdraw unfilled orders;
      the take-profit / stop / trail inputs are 0 (off) and their exits are commented out.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, the sign of a sum of deviations from an SMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG431249 (2 members, best partner #434986, Jaccard 0.918); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431249_sma_deviation_integral"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [170, 85],
    "terms": [18, 9],
}
DEFAULT_PARAMS = {"length": 170, "terms": 18}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    k = c - c.rolling(int(p["length"])).mean()
    s = k.rolling(int(p["terms"]) + 1).sum().to_numpy()
    m = len(s)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if s[i] > 0:
            pos = 1
        elif s[i] < 0:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
