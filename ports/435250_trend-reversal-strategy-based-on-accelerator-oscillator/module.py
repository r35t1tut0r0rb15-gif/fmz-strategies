"""Bill Williams' Accelerator Oscillator sign, broker days: AC above zero holds a long, below zero a short (reversing), at
zero the last side is kept; the "Trade reverse" input flips the side.
Port of FMZ strategy #435250 "Trend Reversal Strategy Based on Accelerator Oscillator" (Accelerator Oscillator (AC) Backtest).

FMZ source id: 435250

Source
    https://www.fmz.com/strategy/435250 (PineScript v2, FMZ last modified 2023-12-13 15:38:12).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 197-213), AC: SMA 5 / 34 of hl2, fast minus slow, minus its SMA 5; reverse input
    nRes = sma(sma(hl2,5) - sma(hl2,34), 5 of the same difference) ... nRes = diff - sma(diff, 5);  pos = nRes > 0 ? 1 : nRes < 0 ? -1 : nz(pos[1], 0);  possig = reverse ? -pos : pos
    possig == 1 -> entry long;  possig == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state holds until the opposite sign; strategy.entry reverses: REVERSAL INTENDED. The
      entry is repeated every bar in the same state (Pine ignores it; a signal is sent on the change
      only). Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG435250 (2 members, best partner #435716, Jaccard 0.901); ND435250 (2 members, best partner #435888, Jaccard 0.733); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435250_accelerator_oscillator_sign"
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
    nf, ns = int(p["fast"]), int(p["slow"])
    diff = hl2.rolling(nf).mean() - hl2.rolling(ns).mean()
    res = (diff - diff.rolling(nf).mean()).to_numpy()
    m = len(res)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if res[i] > 0:
            q = 1
        elif res[i] < 0:
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
