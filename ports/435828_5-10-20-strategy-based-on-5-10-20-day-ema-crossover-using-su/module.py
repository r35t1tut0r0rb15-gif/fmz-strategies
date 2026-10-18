"""Stacked EMAs with the Supertrend direction, broker days: EMA 5 over EMA 10 over EMA 20 with the Supertrend (2, 14) up goes long; the
mirror stack with the Supertrend down goes short (reversing).
Port of FMZ strategy #435828 "基于超趋势的5日10日20日均线交叉策略Strategy-Based-on-5-10-20-Day-EMA-Crossover-Using-Super-Trend-Confirmation" (5-10-20 Cross).

FMZ source id: 435828

Source
    https://www.fmz.com/strategy/435828 (PineScript v4, FMZ last modified 2023-12-19 10:39:36).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 145-183), EMA 5 / 10 / 20; supertrend(2, 14)
    longCondition = ema1 > ema2 and ema1 > ema3 and ema2 > ema3 and ema2 < ema1 and dir == -1;  shortCondition = the mirror and dir == 1;  entry long / short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are states (re-sent every bar); vbt ignores a same-side signal while in a position.
      The Supertrend direction is Pine's built-in (-1 up, 1 down). strategy.entry reverses: REVERSAL
      INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average stack and a trend direction.
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

NAME = "fmz_435828_ema_stack_supertrend"
FAMILY = "supertrend"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [5, 3],
    "mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"len1": 5, "len2": 10, "len3": 20, "mult": 2.0, "atr_len": 14}


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


def _direction(h, lo, c, factor, n):
    """Direction of Pine's built-in supertrend(factor, atrPeriod): -1 up, 1 down."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    dr = np.ones(m)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
        if i == 0 or np.isnan(atr[i - 1]):
            dr[i] = 1
        elif st[i - 1] == ub[i - 1]:
            dr[i] = -1 if cv[i] > ub[i] else 1
        else:
            dr[i] = 1 if cv[i] < lb[i] else -1
        st[i] = lb[i] if dr[i] == -1 else ub[i]
    return dr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    dr = pd.Series(_direction(h, lo, c, float(p["mult"]), int(p["atr_len"])), index=c.index)
    e1 = c.ewm(span=int(p["len1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["len2"]), adjust=False).mean()
    e3 = c.ewm(span=int(p["len3"]), adjust=False).mean()
    le = ((e1 > e2) & (e1 > e3) & (e2 > e3) & (dr == -1)).astype(bool)
    se = ((e1 < e2) & (e1 < e3) & (e2 < e3) & (dr == 1)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
