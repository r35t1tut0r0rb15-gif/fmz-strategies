"""Binomial moving average crosses, broker days: the 10-bar binomial MA crossing above the 30-bar one goes long, crossing
below goes short (reversing). Each MA weights the last n closes by the upper half of the binomial coefficients of degree
2n - 1, the largest on the current bar.
Port of FMZ strategy #434695 "Binomial Moving Average Trend Strategy" (Binomial Moving Average).

FMZ source id: 434695

Source
    https://www.fmz.com/strategy/434695 (PineScript v4, FMZ last modified 2023-12-08 14:55:19).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 149-185), fast 10, slow 30
    hn_ma(price, n): weight of price[j] = C(2n - 1, n - 1 - j) / sum, j = 0 .. n - 1
    crossover(hn_ma(close, 10), hn_ma(close, 30)) -> entry long;  crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The coefficients are fac(2n - 1) / (fac(i - 1) fac(2n - i)), i.e. C(2n - 1, i - 1), set from
      the oldest bar (1) to the newest; the shared coefficient array is reset before each use. The
      port computes the binomial coefficients exactly (for n = 30 the script's 59! exceeds a 64-bit
      integer; the evident intent, the coefficients, is used).
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, weighted average crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() margins stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import math

import numpy as np
import pandas as pd

NAME = "fmz_434695_binomial_ma_cross"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "slow": [30, 20],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30}


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


def _bma(v, n):
    w = np.array([math.comb(2 * n - 1, n - 1 - j) for j in range(n)], dtype=float)   # j = bars back
    w = w / w.sum()
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w[::-1]   # window oldest -> newest
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    cv = bars_df["close"].to_numpy(dtype=float)
    f, s = _bma(cv, int(p["fast"])), _bma(cv, int(p["slow"]))
    f1, s1 = np.concatenate(([np.nan], f[:-1])), np.concatenate(([np.nan], s[:-1]))
    with np.errstate(invalid="ignore"):
        le = (f > s) & (f1 <= s1)
        se = (f < s) & (f1 >= s1)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
