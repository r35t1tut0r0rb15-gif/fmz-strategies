"""P-Signal turns, long only, broker days: the error function of the 8-bar mean / sd of the ohlc4 changes, smoothed over 8 bars; turning up while below zero goes long, turning down while above zero closes.
Port of FMZ strategy #439348 "An Analysis of Quantitative Trading Strategy Based on Gaussian Error Function" (P-Signal Strategy).

FMZ source id: 439348

Source
    https://www.fmz.com/strategy/439348 (PineScript v4, FMZ last modified 2024-01-19 14:28:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 170-203), number of bars 9 (window 8)
    P = sma(erf(sma(change(ohlc4), 8) / stdev(change(ohlc4), 8) / sqrt 2) (erf(1) when the sd is 0), 8);  dP = sign(P - P[1])
    entry long (1) when P < 0 and dP > 0;  close long when P > 0 and dP < 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * erf follows the script's Horner approximation; the standard deviation is Pine's population
      form. While the sd is not yet defined the test sd > 0 is false and the value is erf(1), as
      written. The entry and the close cannot share a bar. Long only. The size of 1 is sizing. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a smoothed statistic of price changes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed size stored.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439348_p_signal_erf_turn_long"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n_points": [9, 15, 25],
}
DEFAULT_PARAMS = {"n_points": 9}


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


def _erf(x):
    """The script's Horner approximation of erf."""
    t = 1.0 / (1.0 + 0.5 * np.abs(x))
    poly = (-x * x - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806
            + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))))
    ans = 1.0 - t * np.exp(poly)
    return np.where(x >= 0, ans, -ans)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["n_points"]) - 1
    ch = ((o + h + lo + c) / 4).diff()
    sd = ch.rolling(n).std(ddof=0)
    mu = ch.rolling(n).mean()
    with np.errstate(divide="ignore", invalid="ignore"):
        arg = np.where(sd > 0, mu / sd / np.sqrt(2), 1.0)
    ps = pd.Series(_erf(arg), index=c.index)            # an undefined sd reads as erf(1), as Pine's na > 0
    ps = ps.rolling(n).mean()
    d = np.sign(ps - ps.shift(1))
    le = (ps < 0) & (d > 0)
    lx = (ps > 0) & (d < 0)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
