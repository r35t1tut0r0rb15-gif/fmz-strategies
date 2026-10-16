"""Noro's Shift Close v1.0, broker days: the close more than 10 % under the SMA 3 of ohlc4 goes long, more than 10 % above
it goes short; back inside the +-10 % band closes everything. Adds are not ported.
Port of FMZ strategy #430259 "Gap Trading Moving Average Strategy" (Noro's Shift Close Strategy v1.0).

FMZ source id: 430259

Source
    https://www.fmz.com/strategy/430259 (PineScript v3, FMZ last modified 2023-10-26 16:05:01).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 153-205), SMA 3 of ohlc4, limit 10 %, pyramiding 5
    ind = (close / sma(ohlc4, 3) - 1) x 100
    ind < -10 -> (close a short) entry long;  ind > 10 -> (close a long) entry short
    -10 < ind < 10 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding = 5: a further signal on the same side adds a lot in the source (the lot is fixed
      while in a position). Adds are not ported (one net position).
    * The three conditions exclude each other: the position is long below the band, short above it
      and flat inside it (a value exactly on a band edge keeps the position).
    * The 1900-2100 window is the author's backtest window: dropped. strategy.entry reverses:
      REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; adds not ported.
    2 generic: PASS, a percentage distance from a moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the lot % and pyramiding 5 stored in original_sizing.txt.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430259_noro_shift_close_v10"
FAMILY = "ma_envelope_reversion"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "limit": [10.0, 5.0, 2.5],
}
DEFAULT_PARAMS = {"limit": 10.0, "ma_len": 3}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    sma = ((o + h + lo + c) / 4).rolling(int(p["ma_len"])).mean()
    ind = ((c / sma - 1) * 100).to_numpy()
    lim = float(p["limit"])
    m = len(ind)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if ind[i] < -lim:
            pos = 1
        elif ind[i] > lim:
            pos = -1
        elif -lim < ind[i] < lim:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
