"""VIDYA (21, CMO 9) direction, daily bars: while VIDYA rises it goes long, while it falls it goes short; reversing.
Port of FMZ strategy #474037 "自适应权重趋势跟踪策略VIDYA多指标组合系统-Adaptive-Weighted-Trend-Following-Strategy-VIDYA-Multi-Indicator-System" (VIDYA Strategy).

FMZ source id: 474037

Source
    https://www.fmz.com/strategy/474037 (PineScript v5, FMZ last modified 2024-12-05 15:07:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-151), length 21; fixed CMO length 9; CMO method
    k = |CMO(9)| / 100;  VIDYA := na(VIDYA[1]) ? src : alpha k src + (1 - alpha k) VIDYA[1];  VIDYA > VIDYA[1] -> entry Go Long;  VIDYA < VIDYA[1] -> entry Go Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The CMO is 100 x (up sum - down sum) / (up sum + down sum) over 9 bars, 0 when na; VIDYA is a
      recursion (a loop) seeded with the source. Entries repeat every bar of a direction and reverse
      on a change. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, adaptive average direction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474037_vidya21_cmo9_direction_reversal"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pds": [21, 50],
}
DEFAULT_PARAMS = {"pds": 21, "cmo_len": 9}


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
    c = bars_df["close"]
    alpha = 2 / (int(p["pds"]) + 1)
    mom = c.diff()
    n = int(p["cmo_len"])
    s1 = mom.clip(lower=0).rolling(n).sum()
    s2 = (-mom).clip(lower=0).rolling(n).sum()
    cmo = (100 * (s1 - s2) / (s1 + s2)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    k = (cmo.abs() / 100).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    v = np.full(len(cv), np.nan)
    for i in range(len(cv)):
        if i == 0 or np.isnan(v[i - 1]):
            v[i] = cv[i]
        else:
            v[i] = alpha * k[i] * cv[i] + (1 - alpha * k[i]) * v[i - 1]
    vs = pd.Series(v, index=bars_df.index)
    le = vs > vs.shift(1)
    se = vs < vs.shift(1)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
