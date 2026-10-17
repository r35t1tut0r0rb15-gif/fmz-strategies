"""Awesome oscillator of Heikin Ashi midpoints, long only, broker days: the oscillator (SMA 5 - SMA 34 of the Heikin Ashi
hl2) rising holds a long, falling closes it (shorts are switched off).
Port of FMZ strategy #432902 "Dual Moving Average Crossover Strategy" (Awesome Oscillator.MMouse_Lager_BCE).

FMZ source id: 432902

Source
    https://www.fmz.com/strategy/432902 (PineScript v2, FMZ last modified 2023-11-22 16:10:21).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 169-217), AO 5 / 34 on Heikin Ashi hl2, shorts off, reverse off
    ao = sma(ha_hl2, 5) - sma(ha_hl2, 34);  pos = ao > ao[1] ? 1 : ao < ao[1] ? -1 : pos[1]
    pos 1 -> entry long;  pos -1 -> close long (allowShorts false)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Heikin Ashi candles are the chart's own (security of the heikinashi ticker, same
      timeframe): high / low are the extremes of the bar with its HA open and close. The RSI of the
      open is computed but not used. The start date (2017) is dropped. Long only; Opposite entries
      cannot occur. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator direction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432902_ha_awesome_oscillator_long"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 3],
    "slow": [34, 21],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 34}


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
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    hc = (o + h + lo + c) / 4
    ho = np.full(len(c), np.nan)
    for i in range(len(c)):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 else (ho[i - 1] + hc[i - 1]) / 2
    hh = np.maximum(h, np.maximum(ho, hc))
    hl = np.minimum(lo, np.minimum(ho, hc))
    mid = pd.Series((hh + hl) / 2, index=bars_df.index)
    ao = (mid.rolling(int(p["fast"])).mean() - mid.rolling(int(p["slow"])).mean()).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    st = 0
    for i in range(1, m):
        if ao[i] > ao[i - 1]:
            st = 1
        elif ao[i] < ao[i - 1]:
            st = -1
        tgt[i] = 1 if st == 1 else 0
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, false, false.copy()))


def portfolio_kwargs(**params):
    return {}
