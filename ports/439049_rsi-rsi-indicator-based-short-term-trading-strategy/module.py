"""RSI 14 crossings, broker days, long only: the RSI crossing up through 30 buys, crossing down through 70 closes.
Port of FMZ strategy #439049 "基于RSI指标的短线交易策略RSI-Indicator-Based-Short-term-Trading-Strategy" (RSI Strategy).

FMZ source id: 439049

Source
    https://www.fmz.com/strategy/439049 (PineScript v4, FMZ last modified 2024-01-17 11:49:15).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 126-157), RSI 14 at 30 / 70; stop 10 %, take 1 % (as order prices); capital 50000 / close quantity
    co = crossover(rsi, 30) -> strategy.order(RsiLE, long, qty, limit = avg x 1.01, stop = avg x 0.9);  cu = crossunder(rsi, 70) -> close RsiLE

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.order's limit and stop are ENTRY prices, not exits: from flat the average price is na, so
      the order is a market buy; while long it adds (sizing), so the port holds one position. The stop /
      take exits are commented out in the source. Long only. The quantity is sizing. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI level crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital / close quantity and the entry-price inputs stored.
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

NAME = "fmz_439049_rsi_30_70_cross_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "over_sold": [30, 20],
}
DEFAULT_PARAMS = {"length": 14, "over_sold": 30.0, "over_bought": 70.0}


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
    r = _rsi(bars_df["close"], int(p["length"]))
    os_, ob = float(p["over_sold"]), float(p["over_bought"])
    co = (r > os_) & (r.shift(1) <= os_)
    cu = (r < ob) & (r.shift(1) >= ob)
    false = pd.Series(False, index=bars_df.index)
    return co, cu & ~co, false, false.copy()


def portfolio_kwargs(**params):
    return {}
