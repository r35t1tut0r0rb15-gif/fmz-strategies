"""DI+ vs DI- side: long while DI+ is above DI-, short while below (always in).
Port of FMZ strategy #361554 "ADX-and-DI-for-v4" (BeikabuOyaji's ADX and DI with orders added).

Source
    https://www.fmz.com/strategy/361554 (PineScript v4, FMZ last modified 2022-05-07 16:31:36).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 44-72), len 14
    TrueRange / DM+ / DM- with nz(previous) (0 before the first bar)
    Smoothed X := nz(Smoothed X[1]) - nz(Smoothed X[1])/len + X      (Wilder running sum)
    DIPlus = SmoothedDM+ / SmoothedTR * 100; DIMinus likewise
    DIPlus > DIMinus -> entry long;  else DIPlus < DIMinus -> entry short
    (ADX is computed but not used by the orders)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The running sums start at 0 with nz(close[1]) = 0 on the first bar, as written; that seed
      fades geometrically. The port emits nothing for the first `len` bars.
    * strategy.entry reverses an opposite position: REVERSAL INTENDED (portfolio_kwargs {};
      the engine's default opposite-entry reversal applies).
    * Daily bars (backtest period 1d) are broker days (17:00 New York).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361554_di_side_reverse"
FAMILY = "directional_movement"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [7, 14, 21],
}
DEFAULT_PARAMS = {"length": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    s_tr = s_p = s_m = 0.0
    pos = 0
    for i in range(m):
        pc = c[i - 1] if i > 0 else 0.0
        ph = h[i - 1] if i > 0 else 0.0
        pl = lo[i - 1] if i > 0 else 0.0
        tr = max(h[i] - lo[i], abs(h[i] - pc), abs(lo[i] - pc))
        up, dn = h[i] - ph, pl - lo[i]
        dmp = max(up, 0.0) if up > dn else 0.0
        dmm = max(dn, 0.0) if dn > up else 0.0
        s_tr = s_tr - s_tr / n + tr
        s_p = s_p - s_p / n + dmp
        s_m = s_m - s_m / n + dmm
        if i < n or s_tr == 0:
            continue
        di_p, di_m = s_p / s_tr * 100, s_m / s_tr * 100
        if di_p > di_m:
            if pos != 1:
                le[i], pos = True, 1
        elif di_p < di_m and pos != -1:
            se[i], pos = True, -1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
