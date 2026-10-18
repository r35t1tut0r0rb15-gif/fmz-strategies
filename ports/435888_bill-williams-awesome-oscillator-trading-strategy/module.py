"""Awesome Oscillator slope, broker days: a rising AO holds a long, a falling AO a short (reversing); a flat AO keeps the last side; the
"Trade reverse" input flips the side.
Port of FMZ strategy #435888 "Bill Williams Awesome Oscillator Trading Strategy" (Bill Williams. Awesome Oscillator (AO)).

FMZ source id: 435888

Source
    https://www.fmz.com/strategy/435888 (PineScript v2, FMZ last modified 2023-12-19 15:27:15).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 169-183), AO = SMA 5 minus SMA 34 of hl2
    pos = ao > ao[1] ? 1 : ao < ao[1] ? -1 : nz(pos[1], 0);  possig = reverse ? -pos : pos;  possig == 1 -> entry long;  possig == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state holds until the opposite slope; the signal is sent on the change of state only.
      strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND435250 (2 members, best partner #435250, Jaccard 0.733); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435888_awesome_oscillator_slope"
FAMILY = "momentum_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "slow": [34, 21],
}
DEFAULT_PARAMS = {"reverse": False, "slow": 34, "fast": 5}


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
    ao = hl2.rolling(int(p["fast"])).mean() - hl2.rolling(int(p["slow"])).mean()
    up = (ao > ao.shift(1)).to_numpy()
    dn = (ao < ao.shift(1)).to_numpy()
    m = len(up)
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
