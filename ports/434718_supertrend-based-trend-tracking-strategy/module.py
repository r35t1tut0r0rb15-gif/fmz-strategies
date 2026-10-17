"""Supertrend 10 / 3 flips, broker days: a flip up goes long, a flip down goes short (reversing).
Port of FMZ strategy #434718 "SuperTrend based Trend Tracking Strategy" (Supertrend Strategy).

FMZ source id: 434718

Source
    https://www.fmz.com/strategy/434718 (PineScript v4, FMZ last modified 2023-12-08 17:07:53).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 140-183), ATR 10 (Wilder, "change ATR" on) x 3 on hl2
    trend flips to 1 -> entry long;  trend flips to -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Supertrend is this script's (KivancOzbilgic form). strategy.entry reverses: REVERSAL
      INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bands.
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

NAME = "fmz_434718_supertrend_10_3_flips"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [3.0, 2.0],
    "atr_len": [10, 20],
}
DEFAULT_PARAMS = {"atr_len": 10, "mult": 3.0}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean().to_numpy()
    mlt = float(p["mult"])
    src = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    up, dn = src - mlt * atr, src + mlt * atr
    trend = np.ones(m, dtype=np.int8)
    for i in range(m):
        up1 = up[i - 1] if i > 0 and not np.isnan(up[i - 1]) else up[i]
        dn1 = dn[i - 1] if i > 0 and not np.isnan(dn[i - 1]) else dn[i]
        cp = cv[i - 1] if i > 0 else np.nan
        if cp > up1:
            up[i] = max(up[i], up1)
        if cp < dn1:
            dn[i] = min(dn[i], dn1)
        t1 = trend[i - 1] if i > 0 else 1
        trend[i] = 1 if (t1 == -1 and cv[i] > dn1) else (-1 if (t1 == 1 and cv[i] < up1) else t1)
    t1 = np.concatenate(([trend[0]], trend[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((trend == 1) & (t1 == -1), index=ix), false,
            pd.Series((trend == -1) & (t1 == 1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
