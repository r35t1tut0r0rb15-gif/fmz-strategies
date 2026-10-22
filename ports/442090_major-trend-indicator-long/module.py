"""Regression-band trend state, broker days, long only: long while the regression of highs + 5-bar highs sits above its offset regression, the regression of lows + 5-bar lows above its own, and the short
close regression above the long one; flat otherwise.
Port of FMZ strategy #442090 "Major Trend Indicator Long" (MTIL).

FMZ source id: 442090

Source
    https://www.fmz.com/strategy/442090 (PineScript v5, FMZ last modified 2024-02-19 11:15:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 119-163), highs / lows 5; linreg 3, 23, 75 with offsets 1, 5, 6; start date 2001
    x_y = linreg(highest(high, 5) + high, 23, 1);  y_x = linreg(lowest(low, 5) + low, 75, 1);  upper = linreg(x_y, 23, 6);  lower = linreg(y_x, 23, 6)
    bull = x_y > upper and y_x > lower and linreg(close, 3, 1) > linreg(close, 75, 5);  bull -> entry Long;  not bull -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's linreg(src, n, offset) is the least-squares line over the last n values evaluated n - 1 -
      offset bars from the oldest, as written. The start date (2001) is always met. The state is a level.
      Long only. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, regression-band states.
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

NAME = "fmz_442090_regression_band_trend_state_long"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "linreg_st1": [23, 15],
    "linreg_lt": [75, 50],
}
DEFAULT_PARAMS = {"linreg_st1": 23, "linreg_lt": 75, "linreg_st": 3, "length_high": 5, "length_low": 5}


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


def _linreg(x, n, off):
    """Pine linreg(x, n, offset): the least-squares line over the last n values at position n - 1 - offset."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.lib.stride_tricks.sliding_window_view(v, n)
        t = np.arange(n, dtype=float)
        tm = t.mean()
        ym = w.mean(axis=1)
        slope = ((w - ym[:, None]) @ (t - tm)) / ((t - tm) ** 2).sum()
        out[n - 1:] = ym + slope * (n - 1 - off - tm)
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    st1, lt = int(p["linreg_st1"]), int(p["linreg_lt"])
    xi = h.rolling(int(p["length_high"])).max()
    yi = lo.rolling(int(p["length_low"])).min()
    x_y = _linreg(xi + h, st1, 1)
    y_x = _linreg(yi + lo, lt, 1)
    upper = _linreg(x_y, st1, 6)
    lower = _linreg(y_x, st1, 6)
    bull = (x_y > upper) & (y_x > lower) & (_linreg(c, int(p["linreg_st"]), 1) > _linreg(c, lt, 5))
    false = pd.Series(False, index=c.index)
    return bull, ~bull, false, false.copy()


def portfolio_kwargs(**params):
    return {}
