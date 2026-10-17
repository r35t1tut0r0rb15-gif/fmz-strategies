"""Rational-quadratic kernel envelopes of log prices, broker days, long only: the close crossing above the kernel estimate of
the lows goes long; the kernel estimate of the highs crossing above the close (the close falling under it) closes the long.
Port of FMZ strategy #435010 "Momentum Tracking Adaptive Statistical Arbitrage Strategy" (Nadaraya-Watson Envelope Strategy).

FMZ source id: 435010

Source
    https://www.fmz.com/strategy/435010 (PineScript v5, FMZ last modified 2023-12-11 16:41:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 107-178), kernel look back 8, relative weighting 8, start at bar 25; ATR bands plotted only
    kernel(x) = sum_{i=0..8} w_i x[i] / sum w_i,  w_i = (1 + (25 - i)^2 / (2 x 8 x 8^2))^-8;  envLow / envHigh = exp(kernel(log low / log high))
    crossover(close, envLow) -> entry long;  crossover(envHigh, close) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The kernel weights the last 9 bars, the older ones slightly more (x_0 = 25 lies beyond the
      window), as written. The ATR envelope bounds are drawing only. pyramiding 1. Long only. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, kernel-smoothed price levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 20 % of equity stored.
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

NAME = "fmz_435010_nadaraya_watson_kernel_long"
FAMILY = "mean_reversion_band"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "h": [8, 16],
    "x0": [25, 8],
}
DEFAULT_PARAMS = {"h": 8, "alpha": 8.0, "x0": 25}


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


def _kernel(v, hh, alpha, x0):
    i = np.arange(hh + 1)
    w = (1 + (x0 - i) ** 2 / (2 * alpha * hh * hh)) ** (-alpha)       # w[i] for x[i], i bars back
    out = np.full(len(v), np.nan)
    if len(v) > hh:
        out[hh:] = np.lib.stride_tricks.sliding_window_view(v, hh + 1) @ (w[::-1] / w.sum())
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hh, al, x0 = int(p["h"]), float(p["alpha"]), float(p["x0"])
    cv = bars_df["close"].to_numpy(dtype=float)
    env_l = np.exp(_kernel(np.log(bars_df["low"].to_numpy(dtype=float)), hh, al, x0))
    env_h = np.exp(_kernel(np.log(bars_df["high"].to_numpy(dtype=float)), hh, al, x0))
    c1 = np.concatenate(([np.nan], cv[:-1]))
    l1, h1 = np.concatenate(([np.nan], env_l[:-1])), np.concatenate(([np.nan], env_h[:-1]))
    with np.errstate(invalid="ignore"):
        le = (cv > env_l) & (c1 <= l1)
        lx = (env_h > cv) & (h1 <= c1)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx & ~le, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
