"""Directional movement dominance with a 3-point dead band, broker days: +DI over -DI by more than 3 points holds a long, -DI over +DI by
more than 3 a short (reversing); inside the band the last side is kept.
Port of FMZ strategy #435871 "Directional Movement Index Dual direction Trading Strategy" (Noro's DI Strategy).

FMZ source id: 435871

Source
    https://www.fmz.com/strategy/435871 (PineScript v3, FMZ last modified 2023-12-19 14:13:52).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 258-291), DI length 14, limit 3 points; sums smoothed as S = S[1] - S[1] / len + x
    DIPlus = smoothed(+DM) / smoothed(TR) 100;  DIMinus likewise;  trend = DIPlus > DIMinus + 3 ? 1 : DIPlus < DIMinus - 3 ? -1 : trend[1]
    trend == 1 -> entry long;  trend == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The smoothing is the script's own running sum (no division by the length in the result, which
      cancels in the DI ratio). The previous high / low / close are zero before the first bar (nz), as written.
      The date window is the default 1900-2100: always true. The signal is sent on the change of
      trend only. strategy.entry reverses: REVERSAL INTENDED. The equity-based lot is sizing. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, directional movement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-based lot, capital percent and pyramiding inputs stored.
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

NAME = "fmz_435871_noro_di_dominance"
FAMILY = "trend_confluence"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [14, 20],
    "limit": [3, 5],
}
DEFAULT_PARAMS = {"len": 14, "limit": 3}


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
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    n = int(p["len"])
    lim = float(p["limit"])
    m = len(c)
    str_ = sp = sm = 0.0
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        h1 = h[i - 1] if i > 0 else 0.0
        l1 = lo[i - 1] if i > 0 else 0.0
        c1 = c[i - 1] if i > 0 else 0.0
        tr = max(max(h[i] - lo[i], abs(h[i] - c1)), abs(lo[i] - c1))
        dmp = max(h[i] - h1, 0.0) if (h[i] - h1) > (l1 - lo[i]) else 0.0
        dmm = max(l1 - lo[i], 0.0) if (l1 - lo[i]) > (h[i] - h1) else 0.0
        str_ = str_ - str_ / n + tr
        sp = sp - sp / n + dmp
        sm = sm - sm / n + dmm
        if str_ != 0:
            dip, dim = sp / str_ * 100, sm / str_ * 100
            if dip > dim + lim:
                q = 1
            elif dip < dim - lim:
                q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
