"""Trend confidence crosses, broker days: the slope of the 30-bar regression of the close divided by the fit's residual
deviation crossing above 0.25 goes long and back under -0.10 closes it; crossing under -0.25 goes short and back above
-0.05 covers. The 10 % stop orders are, as written, placed before the entry fills and so carry no level.
Port of FMZ strategy #432898 "Trend Following Strategy Based on Trend Confidence" (Trend Following based on Trend Confidence).

FMZ source id: 432898

Source
    https://www.fmz.com/strategy/432898 (PineScript v5, FMZ last modified 2023-11-22 15:50:07).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 151-208), length 30, long 0.25 / -0.10, short -0.25 / -0.05, stop 10 %
    slope = linreg(close, 30, 0) - linreg(close, 30, 1);  deviation = rms of the 30 residuals;  tc = slope / deviation (the price divides out)
    crossover(tc, 0.25) -> entry long, exit(stop = avg price x 0.9);  crossunder(tc, -0.10) -> close long
    crossunder(tc, -0.25) -> entry short, exit(stop = avg price x 1.1);  crossover(tc, -0.05) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * AS WRITTEN: the stop order is issued on the signal bar with strategy.position_avg_price of that
      bar, i.e. before the entry fills: from flat it is na (no stop), from the opposite side it is
      that side's price. Ported without the stop (as written in effect); listed with the as-written
      ports (the intended 10 % stop from the fill is owed).
    * The closes act on the position held at the bar's start; an opposite entry reverses and a later
      close of the other side does not undo it: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a scale-free slope-to-noise ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the stop orders quoted in original_sizing.txt.
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

NAME = "fmz_432898_trend_confidence_cross"
FAMILY = "slope_momentum"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [30, 15],
    "long_entry": [0.25, 0.5],
}
DEFAULT_PARAMS = {"length": 30, "long_entry": 0.25, "long_exit": -0.10, "short_entry": -0.25, "short_exit": -0.05}


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


def _trend_confidence(c, n):
    v = c.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        t = np.arange(n, dtype=float) - (n - 1) / 2.0
        slope = win @ t / float(t @ t)
        fit = win.mean(axis=1)[:, None] + slope[:, None] * t[None, :]
        dev = np.sqrt(((win - fit) ** 2).mean(axis=1))
        with np.errstate(divide="ignore", invalid="ignore"):
            out[n - 1:] = slope / dev
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    tc = _trend_confidence(c, int(p["length"]))
    xo = lambda a: (tc > a) & (tc.shift(1) <= a)  # noqa: E731
    xu = lambda a: (tc < a) & (tc.shift(1) >= a)  # noqa: E731
    el, xl = xo(float(p["long_entry"])).to_numpy(), xu(float(p["long_exit"])).to_numpy()
    es, xs = xu(float(p["short_entry"])).to_numpy(), xo(float(p["short_exit"])).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if el[i]:
            pos = 1
        if xl[i] and start == 1 and pos == 1:
            pos = 0
        if es[i]:
            pos = -1
        if xs[i] and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
