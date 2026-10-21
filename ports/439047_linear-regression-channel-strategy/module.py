"""Dips under a linear-regression band with a Hull 400 filter, broker days, long only: a close 2 % under the 55-bar regression line while above the Hull MA 400 buys; a close above the regression line closes.
Port of FMZ strategy #439047 "Linear Regression Channel Strategy" (Linear Channel).

FMZ source id: 439047

Source
    https://www.fmz.com/strategy/439047 (PineScript v4, FMZ last modified 2024-01-17 11:41:16).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 170-193), linreg 55, band -2 %; Hull 400; 100 % of equity, commission 0.075 %; date window true
    linreg = linreg(close, 55, 0);  band = linreg x (1 - 2 %);  close < band and hma(close, 400) < close -> entry BUY;  close > linreg -> close BUY

Interpretation choices (Pine rules in SURVEY_README.md)
    * linreg is the current value of the 55-bar least-squares line. The Hull MA uses floor(n / 2) and
      round(sqrt(n)). _testPeriod() is true. Long only. The size and commission are sizing / costs. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, regression band and Hull filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
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

NAME = "fmz_439047_linreg_band_dip_hull_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [55, 100],
    "hma_len": [400, 200],
}
DEFAULT_PARAMS = {"length": 55, "hma_len": 400, "value": -2.0}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(x, n):
    return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(np.floor(np.sqrt(n) + 0.5)))


def _linreg(y, n, offset=0):
    t = np.arange(n, dtype=float)

    def _fit(a):
        b, a0 = np.polyfit(t, a, 1)
        return a0 + b * (n - 1 - offset)

    return y.rolling(n).apply(_fit, raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    lr = _linreg(c, int(p["length"]))
    band = lr * (float(p["value"]) / 100 + 1)
    hma = _hma(c, int(p["hma_len"]))
    le = (c < band) & (hma < c)
    lx = c > lr
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
