"""Ehlers bandpass filter (HPotter), broker days: the filter of hl2 (period 20, delta 0.5) above +zone holds a long, at or
below -zone holds a short; the price-unit zones become ATR multiples.
Port of FMZ strategy #430069 "Dual Bandpass Filter Strategy" (Bandpass Filter Strategy ver 2.0).

FMZ source id: 430069

Source
    https://www.fmz.com/strategy/430069 (PineScript v2, FMZ last modified 2023-10-24 17:00:02).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 186-221), length 20, delta 0.5, SellZone 5, BuyZone -5
    beta = cos(3.14 x (360 / L) / 180); gamma = 1 / cos(3.14 x (720 x Delta / L) / 180); alpha = gamma - sqrt(gamma^2 - 1)
    BP = 0.5 (1 - alpha)(hl2 - hl2[2]) + beta (1 + alpha) nz(BP[1]) - alpha nz(BP[2])
    BP > SellZone -> 1 (entry long);  BP <= BuyZone -> -1 (entry short);  else pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: SellZone 5 / BuyZone -5 are price units; they become +-zone_atr x Wilder ATR(14) of
      the same bar (as #362638).
    * "Trade reverse" defaults to false and is fixed. strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the price-unit zones -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430069 (3 members, best partner #437527, Jaccard 0.697); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430069_bandpass_filter_zones"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "length": [20, 40],
    "zone_atr": [0.1, 0.5],
}
DEFAULT_PARAMS = {"length": 20, "delta": 0.5, "zone_atr": 0.1}


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


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n, delta = int(p["length"]), float(p["delta"])
    x = ((bars_df["high"] + bars_df["low"]) / 2).to_numpy(dtype=float)
    zone = (float(p["zone_atr"]) * _atr(bars_df, ATR_LEN)).to_numpy()
    beta = np.cos(3.14 * (360 / n) / 180)
    gamma = 1 / np.cos(3.14 * (720 * delta / n) / 180)
    alpha = gamma - np.sqrt(gamma * gamma - 1)
    m = len(x)
    bp = np.zeros(m)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if i >= 2:
            bp[i] = 0.5 * (1 - alpha) * (x[i] - x[i - 2]) + beta * (1 + alpha) * bp[i - 1] - alpha * bp[i - 2]
            if bp[i] > zone[i]:
                pos = 1
            elif bp[i] <= -zone[i]:
                pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
