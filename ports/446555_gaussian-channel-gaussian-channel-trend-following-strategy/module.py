"""Ehlers Gaussian channel breakouts (4 poles, period 144, filtered true range x 1.414 on hlc3), daily bars, long only: the close crossing over the upper band goes long, crossing back under it closes.
Port of FMZ strategy #446555 "Gaussian-Channel趋势追踪策略-Gaussian-Channel-Trend-Following-Strategy" (Gaussian Channel Strategy v2.0).

FMZ source id: 446555

Source
    https://www.fmz.com/strategy/446555 (PineScript v5, FMZ last modified 2024-03-29 16:26:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-252), source hlc3; poles 4; sampling period 144; TR multiplier 1.414; reduced lag and fast modes off; dates 2018-2060 (always true); 100 % of equity, capital 1000, commission 0.1 %, slippage 3
    beta = (1 - cos(2 pi / 144)) / (1.414^(2/4) - 1);  alpha = -beta + sqrt(beta^2 + 2 beta);  filt / filttr = 4-pole Gaussian filter of hlc3 / ta.tr(true)
    hband = filt + 1.414 filttr;  crossover(close, hband) -> entry long;  crossunder(close, hband) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The version-5 rewrite of #446461 (same filter, inputs and orders), a near-duplicate in the corpus
      ported under rule 7. The N-pole filter is the script's recursion with nz() seeds, applied to hlc3
      and to ta.tr(true) (the first bar's range is high - low); the f_pole bug that computes the 7-pole
      filter for 2+ poles never reaches the 4-pole output. Both lag modes are off; timeCondition is
      true. Long only. The 100 % of equity size is sizing; the commission and slippage are costs (not
      ported). FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the recursive filter uses past values only.
    2 generic: PASS, Gaussian channel breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 100 % of equity size stored; the commission and slippage are costs, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND446461 (2 members, best partner #446461, Jaccard 0.749); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import math

import numpy as np
import pandas as pd

NAME = "fmz_446555_gaussian_channel_v2_upper_break_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "poles": [4, 2],
    "period": [144, 72],
}
DEFAULT_PARAMS = {"poles": 4, "period": 144, "mult": 1.414}


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


def _gauss(s, a, n):
    """f_filt9x as written: an n-pole recursion with nz() seeds."""
    v = np.nan_to_num(s, nan=0.0)
    m = len(v)
    f = np.zeros(m)
    x = 1.0 - a
    w = [((-1) ** (k + 1)) * math.comb(n, k) * x ** k for k in range(1, n + 1)]
    an = a ** n
    for i in range(m):
        acc = an * v[i]
        for k in range(1, n + 1):
            if i - k >= 0:
                acc += w[k - 1] * f[i - k]
        f[i] = acc
    return f


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, per = int(p["poles"]), int(p["period"])
    beta = (1 - math.cos(2 * math.pi / per)) / (1.414 ** (2 / n) - 1)
    alpha = -beta + math.sqrt(beta ** 2 + 2 * beta)
    src = ((h + lo + c) / 3).to_numpy(dtype=float)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # tr(true): bar 0 is high - low
    filt = _gauss(src, alpha, n)
    ftr = _gauss(tr.to_numpy(dtype=float), alpha, n)
    hb = pd.Series(filt + ftr * float(p["mult"]), index=c.index)
    c1 = c.shift(1)
    le = (c > hb) & (c1 <= hb.shift(1))
    lx = (c < hb) & (c1 >= hb.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
