"""Noro's fishnet of Jurik-style averages, broker days: the 10-bar average above the 200-bar one is long, below is short (the earlier side holds on a tie); entries are sent on every bar of the trend, reversing.
Port of FMZ strategy #437558 "Grid Trading Strategy Based on Moving Average System" (Fishnet str).

FMZ source id: 437558

Source
    https://www.fmz.com/strategy/437558 (PineScript v3, FMZ last modified 2024-01-03 17:18:22).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 151-228), JMA-style averages 10 ... 200 of the close (only 10 and 200 used by the orders); colour filter off; long and short on
    jmax(src, len): beta = 0.45 (len - 1) / (0.45 (len - 1) + 2), alpha = beta^3, L0..L4 recursions with nz();  trend = ma01 > ma20 ? 1 : ma01 < ma20 ? -1 : trend[1]
    trend == 1 -> entry Long;  trend == -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The averages follow the script's recursion (nz seeds at 0, so they start from 0 and converge), as
      written. The 18 middle averages are plotted only. The trend is a level, so the entry is sent on every
      bar of it; a same-side entry while in the position is ignored (pyramiding 0). The colour filter is
      off and the date range covers everything. REVERSAL INTENDED. The lot is sizing. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average comparison.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-based lot stored.
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

NAME = "fmz_437558_noro_fishnet_jma_trend"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_len": [10, 20],
    "slow_len": [200, 100],
}
DEFAULT_PARAMS = {"fast_len": 10, "slow_len": 200}


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


def _jmax(src, n):
    beta = 0.45 * (n - 1) / (0.45 * (n - 1) + 2)
    alpha = beta ** 3
    v = src.to_numpy(dtype=float)
    m = len(v)
    out = np.full(m, np.nan)
    l0 = l1 = l3 = l4 = 0.0
    for i in range(m):
        l0 = (1 - alpha) * v[i] + alpha * l0
        l1 = (v[i] - l0) * (1 - beta) + beta * l1
        l2 = l0 + l1
        l3 = (l2 - l4) * ((1 - alpha) * (1 - alpha)) + (alpha * alpha) * l3
        l4 = l4 + l3
        out[i] = l4
        l0, l1, l3, l4 = (0.0 if np.isnan(x) else x for x in (l0, l1, l3, l4))
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a, b = _jmax(c, int(p["fast_len"])), _jmax(c, int(p["slow_len"]))
    m = len(a)
    tr = np.zeros(m)
    t = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if a[i] > b[i]:
                t = 1.0
            elif a[i] < b[i]:
                t = -1.0
            tr[i] = t
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(tr == 1, index=ix), false, pd.Series(tr == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
