"""Noro's RSI symphony, broker days, long only: any of five RSIs (4, 7, 14, 21, 28) under its own limit (15, 20, 25, 30, 35) buys; all five above their limits close the long.
Port of FMZ strategy #437399 "多重RSI指标聚合策略Strategy-of-Synthesis-between-Multiple-Relative-Strength-Indicators" (Symphony 1.0).

FMZ source id: 437399

Source
    https://www.fmz.com/strategy/437399 (PineScript v2, FMZ last modified 2024-01-02 12:06:14).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 189-242), RSI 1-5 periods 4 / 7 / 14 / 21 / 28, limits 15 / 20 / 25 / 30 / 35, all on; colour filter off; pyramiding 20
    up = rsi1 < 15 or rsi2 < 20 or rsi3 < 25 or rsi4 < 30 or rsi5 < 35 -> entry Long (adds up to pyramiding 20);  exit = every rsi above its limit -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The adds that pyramiding 20 allows are sizing: the port holds one position (repeats ignored). The short
      input is never used by an order: long only. The colour filter is off; the date range covers
      everything: dropped. Long only. The lot is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 20 and the equity-based lot stored.
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

NAME = "fmz_437399_noro_rsi_symphony_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_period1": [4, 3],
    "rsi_limit1": [15.0, 10.0],
}
DEFAULT_PARAMS = {"rsi_period1": 4, "rsi_limit1": 15.0, "rsi_period2": 7, "rsi_limit2": 20.0, "rsi_period3": 14,
                  "rsi_limit3": 25.0, "rsi_period4": 21, "rsi_limit4": 30.0, "rsi_period5": 28, "rsi_limit5": 35.0}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    up = pd.Series(False, index=c.index)
    ex = pd.Series(True, index=c.index)
    for k in range(1, 6):
        r = _rsi(c, int(p[f"rsi_period{k}"]))
        lim = float(p[f"rsi_limit{k}"])
        up = up | (r < lim)
        ex = ex & (r > lim)
    false = pd.Series(False, index=bars_df.index)
    return up, ex, false, false.copy()


def portfolio_kwargs(**params):
    return {}
