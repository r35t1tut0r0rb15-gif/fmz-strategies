"""Laguerre RSI zones, broker days: the Laguerre-filter RSI (gamma 0.5) above 0.8 turns the state long, below 0.2 short,
otherwise it stays; always in the state's direction.
Port of FMZ strategy #432920 "Modern Laguerre Transform Relative Strength Index Optimization Strategy" (Laguerre-based RSI (HPotter)).

FMZ source id: 432920

Source
    https://www.fmz.com/strategy/432920 (PineScript v2, FMZ last modified 2023-11-22 17:38:16).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 117-137), gamma 0.5, bands 0.8 / 0.2, reverse false
    L0 = (1 - g) close + g nz(L0[1], 1);  Lk = -g L(k-1) + nz(L(k-1)[1], 1) + g nz(Lk[1], 1)
    rsi = CU / (CU + CD) (0 when both are 0);  pos = rsi > 0.8 ? 1 : rsi < 0.2 ? -1 : pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * The filter states start at 1 (nz(.., 1)), as written. strategy.entry reverses: REVERSAL
      INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a bounded oscillator.
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

NAME = "fmz_432920_laguerre_rsi_zones"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "gamma": [0.5, 0.7],
    "band": [0.8, 0.7],
}
DEFAULT_PARAMS = {"gamma": 0.5, "band": 0.8}


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
    cv = bars_df["close"].to_numpy(dtype=float)
    g = float(p["gamma"])
    bb, sb = float(p["band"]), 1 - float(p["band"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    l0 = l1 = l2 = l3 = 1.0
    pos = 0
    for i in range(m):
        n0 = (1 - g) * cv[i] + g * l0
        n1 = -g * n0 + l0 + g * l1
        n2 = -g * n1 + l1 + g * l2
        n3 = -g * n2 + l2 + g * l3
        l0, l1, l2, l3 = n0, n1, n2, n3
        cu = (l0 - l1 if l0 >= l1 else 0) + (l1 - l2 if l1 >= l2 else 0) + (l2 - l3 if l2 >= l3 else 0)
        cd = (0 if l0 >= l1 else l1 - l0) + (0 if l1 >= l2 else l2 - l1) + (0 if l2 >= l3 else l3 - l2)
        r = cu / (cu + cd) if cu + cd != 0 else 0.0
        if r > bb:
            pos = 1
        elif r < sb:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
