"""Empirical mode decomposition state, broker days: the mean of the band-pass filter (period 20) over both its scaled peak and valley averages holds a long, under both a short (reversing); between
them the last side is kept; the "Trade reverse" input flips the side.
Port of FMZ strategy #436246 "Empirical Mode Decomposition Based Quantitative Trading Strategy" (Empirical Mode Decomposition).

FMZ source id: 436246

Source
    https://www.fmz.com/strategy/436246 (PineScript v2, FMZ last modified 2023-12-22 14:41:34).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 119-142), length 20, delta 0.5, fraction 0.1
    bp = 0.5 (1 - alpha) (hl2 - hl2[2]) + beta (1 + alpha) bp[1] - alpha bp[2];  xMean = sma(bp, 40);  peak / valley = bp[1] at local peaks / valleys;  pos = xMean over both 0.1 x averages ? 1 : under both ? -1 : last;  possig = reverse ? -pos : pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * beta = cos(3.1415 x (360 / Length) / 180), gamma = 1 / cos(3.1415 x (720 Delta / Length) / 180), alpha = gamma -
      sqrt(gamma^2 - 1), with the author's pi of 3.1415; the filter starts from zero. The signal is sent on the
      change of state only. REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band-pass filter state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430069 (3 members, best partner #437527, Jaccard 0.661); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import math

import numpy as np
import pandas as pd

NAME = "fmz_436246_empirical_mode_state"
FAMILY = "cycle_filter"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "length": [20, 30],
}
DEFAULT_PARAMS = {"reverse": False, "length": 20, "delta": 0.5, "fraction": 0.1}


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
    hl2 = (bars_df["high"] + bars_df["low"]) / 2
    length, delta, fraction = int(p["length"]), float(p["delta"]), float(p["fraction"])
    beta = math.cos(3.1415 * (360 / length) / 180)
    gamma = 1 / math.cos(3.1415 * (720 * delta / length) / 180)
    alpha = gamma - math.sqrt(gamma * gamma - 1)
    x = hl2.to_numpy(dtype=float)
    m = len(x)
    bp = np.zeros(m)
    for i in range(m):
        b1 = bp[i - 1] if i >= 1 else 0.0
        b2 = bp[i - 2] if i >= 2 else 0.0
        x2 = x[i - 2] if i >= 2 else np.nan
        bp[i] = 0.5 * (1 - alpha) * (x[i] - x2) + beta * (1 + alpha) * b1 - alpha * b2
    mean = pd.Series(bp, index=hl2.index).rolling(2 * length).mean()
    peak, valley = np.zeros(m), np.zeros(m)
    for i in range(m):
        pp = peak[i - 1] if i >= 1 else 0.0
        vv = valley[i - 1] if i >= 1 else 0.0
        if i >= 2 and bp[i - 1] > bp[i] and bp[i - 1] > bp[i - 2]:
            pp = bp[i - 1]
        if i >= 2 and bp[i - 1] < bp[i] and bp[i - 1] < bp[i - 2]:
            vv = bp[i - 1]
        peak[i], valley[i] = pp, vv
    nap = pd.Series(peak, index=hl2.index).rolling(50).mean() * fraction
    nav = pd.Series(valley, index=hl2.index).rolling(50).mean() * fraction
    up = ((mean > nap) & (mean > nav)).to_numpy()
    dn = ((mean < nap) & (mean < nav)).to_numpy()
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        tgt[i] = q
    if p["reverse"]:
        tgt = -tgt
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
