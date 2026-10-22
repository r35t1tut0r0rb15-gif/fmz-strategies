"""EMA 6 / JMA 14 crossings, broker days, long only (the default trade type): the EMA 6 crossing over the Jurik-style MA 14 goes long, crossing under closes.
Port of FMZ strategy #440980 "Dual Moving Average Cross Timeframe Trading Strategy" (Multi MA SandBox).

FMZ source id: 440980

Source
    https://www.fmz.com/strategy/440980 (PineScript v4, FMZ last modified 2024-02-04 15:03:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-306), trades LONG; fast EMA 6, slow JMA 14, both on the chart's timeframe; stop / take profit off
    JMA: beta = 0.45 (len - 1) / (0.45 (len - 1) + 2), alpha = beta, a chain of recursive filters (tmp0 .. tmp4, nz starts);  long = crossover(ema6, jma14) -> entry long;  longClose = crossunder -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both security calls use an empty resolution, which is the chart's own timeframe. The JMA chain
      keeps its nz() starts as written. The stop / take-profit block is off. Long only. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA / JMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_440980_ema6_jma14_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lenma_fast": [6, 12],
    "lenma_slow": [14, 28],
}
DEFAULT_PARAMS = {"lenma_fast": 6, "lenma_slow": 14}


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


def _jma(src, n):
    beta = 0.45 * (n - 1) / (0.45 * (n - 1) + 2)
    a = beta
    s = src.to_numpy(dtype=float)
    out = np.full(len(s), np.nan)
    t0 = t1 = t3 = t4 = 0.0
    for i in range(len(s)):
        t0 = (1 - a) * s[i] + a * t0
        t1 = (s[i] - t0) * (1 - beta) + beta * t1
        t2 = t0 + t1
        t3 = (t2 - t4) * ((1 - a) * (1 - a)) + (a * a) * t3
        t4 = t4 + t3
        out[i] = t4
    return pd.Series(out, index=src.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["lenma_fast"]), adjust=False).mean()
    s = _jma(c, int(p["lenma_slow"]))
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
