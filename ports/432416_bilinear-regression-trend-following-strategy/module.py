"""Fast / slow regression-line spread, long only, broker days: the 13-bar regression value minus the 55-bar one crossing
above zero with the close above the EMA 200 goes long; crossing below zero closes it.
Port of FMZ strategy #432416 "Bilinear Regression Trend Following Strategy" (Linear trend).

FMZ source id: 432416

Source
    https://www.fmz.com/strategy/432416 (PineScript v4, FMZ last modified 2023-11-17 16:51:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 158-182), linreg 13 / 55, lags 0, threshold 0, EMA 200
    lr = linreg(close, 13, 0) - linreg(close, 55, 0)
    crossover(lr, 0) and close > ema(close, 200) -> entry long;  crossunder(lr, 0) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * linreg(x, n, 0) is the least-squares line through the last n closes, read at the current bar.
      The test period (from 2017-12-17) is the author's window: dropped. Long only; Opposite entries
      cannot occur. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, regression-line spread sign and an EMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the commission stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432416_linreg_spread_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [13, 8],
    "slow": [55, 34],
}
DEFAULT_PARAMS = {"fast": 13, "slow": 55, "trend": 200}


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


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line through the last n values, read at the last."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        t = np.arange(n, dtype=float) - (n - 1) / 2.0
        slope = win @ t / float(t @ t)
        out[n - 1:] = win.mean(axis=1) + slope * (n - 1) / 2.0
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    lr = _linreg(c, int(p["fast"])) - _linreg(c, int(p["slow"]))
    e = c.ewm(span=int(p["trend"]), adjust=False).mean()
    le = ((lr > 0) & (lr.shift(1) <= 0) & (c > e)).astype(bool)
    lx = ((lr < 0) & (lr.shift(1) >= 0)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
