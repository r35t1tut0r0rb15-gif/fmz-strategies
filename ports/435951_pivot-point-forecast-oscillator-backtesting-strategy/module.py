"""Chande Forecast Oscillator sign, broker days: the close over its 14-bar regression value holds a long, under it a short (reversing); the
"Trade reverse" input flips the side.
Port of FMZ strategy #435951 "Pivot Point Forecast Oscillator Backtesting Strategy" (Chande Forecast Oscillator Backtest).

FMZ source id: 435951

Source
    https://www.fmz.com/strategy/435951 (PineScript v2, FMZ last modified 2023-12-20 13:44:26).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 169-182), linreg length 14, offset 0
    xCFO = (close - linreg(close, 14, 0)) 100 / close;  pos = xCFO > 0 ? 1 : xCFO < 0 ? -1 : nz(pos[1], 0);  possig = reverse ? -pos : pos;  entry long / short

Interpretation choices (Pine rules in SURVEY_README.md)
    * linreg is the value at the end of the least-squares line over the last 14 bars. The signal is
      sent on the change of state only. strategy.entry reverses: REVERSAL INTENDED. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, regression oscillator.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435951_chande_forecast_sign"
FAMILY = "momentum_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "length": [14, 21],
}
DEFAULT_PARAMS = {"reverse": False, "length": 14}


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


def _linreg_end(c, n):
    x = np.arange(n, dtype=float)
    xm = x.mean()
    sxx = ((x - xm) ** 2).sum()

    def f(a):
        return a.mean() + (np.dot(x - xm, a) / sxx) * (n - 1 - xm)

    return c.rolling(n).apply(f, raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    cfo = ((c - _linreg_end(c, int(p["length"]))) * 100 / c).to_numpy()
    m = len(cfo)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if cfo[i] > 0:
            q = 1
        elif cfo[i] < 0:
            q = -1
        tgt[i] = q
    if p["reverse"]:
        tgt = -tgt
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
