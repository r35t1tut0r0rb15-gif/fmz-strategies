"""Supertrend flips with a linear-regression filter, broker days, long only: the Supertrend (3, 14) turning up with the close over the
101-bar least-squares moving average goes long; the Supertrend turning down closes the long.
Port of FMZ strategy #435707 "超级趋势-LSMA-多头策略Super-Trend-LSMA-Long-Strategy" (Supertrend LSMA long Strategy).

FMZ source id: 435707

Source
    https://www.fmz.com/strategy/435707 (PineScript v4, FMZ last modified 2023-12-18 10:43:14).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 141-173), supertrend(3, 14); linreg(close, 101, 0)
    change(direction) < 0 and close > linreg(close, 101, 0) -> entry long;  change(direction) > 0 -> close long   (the date window is 2010-2031)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The least-squares moving average is the value at the end of the regression line over the last
      101 bars. The date window is the author's backtest range: dropped. Long only. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Supertrend and a regression average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435707_supertrend_lsma_long"
FAMILY = "supertrend"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "lengthx": [101, 50],
}
DEFAULT_PARAMS = {"factor": 3.0, "atr_period": 14, "lengthx": 101}


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


def _linreg_end(c, n):
    x = np.arange(n, dtype=float)
    xm = x.mean()
    sxx = ((x - xm) ** 2).sum()

    def f(a):
        return a.mean() + (np.dot(x - xm, a) / sxx) * (n - 1 - xm)

    return c.rolling(n).apply(f, raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    dr = _direction(h, lo, c, float(p["factor"]), int(p["atr_period"]))
    d1 = np.concatenate(([dr[0]], dr[:-1]))
    lsma = _linreg_end(c, int(p["lengthx"]))
    ix = bars_df.index
    flip_up = pd.Series(dr - d1 < 0, index=ix)
    flip_dn = pd.Series(dr - d1 > 0, index=ix)
    false = pd.Series(False, index=ix)
    return (flip_up & (c > lsma)).fillna(False).astype(bool), flip_dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
