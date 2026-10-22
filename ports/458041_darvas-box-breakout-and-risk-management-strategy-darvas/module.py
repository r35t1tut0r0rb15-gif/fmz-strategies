"""Darvas box breakouts, daily bars, long only: the close crossing over the box top buys; crossing under the box bottom sells.
Port of FMZ strategy #458041 "Darvas-Box-Breakout-and-Risk-Management-Strategy-Darvas-盒子突破与风险管理策略" (Darvas Box Strategy).

FMZ source id: 458041

Source
    https://www.fmz.com/strategy/458041 (PineScript v5, FMZ last modified 2024-07-29 14:22:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 229-271), box length 5; 100 % of equity
    NH = valuewhen(high > highest(high, 5)[1], high, 0);  box set when barssince(new high) == 3 and highest(high, 3) < highest(high, 4): top = NH, bottom = lowest(low, 5)
    crossover(close, top) -> entry Buy;  crossunder(close, bottom) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The box follows the classic Darvas script as written: a new high starts a count, and three bars
      later (with the last three highs under the last four) the box top is that high and the bottom is
      the 5-bar low; both hold until the next box. Long only. The 100 % of equity is sizing. FREQ = "1D"
      from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Darvas box breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity sizing stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458041_darvas_box_breakout_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "boxp": [5, 8],
}
DEFAULT_PARAMS = {"boxp": 5}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    b = int(p["boxp"])
    ll = lo.rolling(b).min().to_numpy()
    k1 = h.rolling(b).max()
    k2 = h.rolling(b - 1).max().to_numpy()
    k3 = h.rolling(b - 2).max().to_numpy()
    newhigh = (h > k1.shift(1)).to_numpy()
    hv = h.to_numpy(dtype=float)
    m = len(hv)
    top, bot = np.full(m, np.nan), np.full(m, np.nan)
    nh = tp = bt = np.nan
    last_nh = -1
    for i in range(m):
        if newhigh[i]:
            nh, last_nh = hv[i], i
        if last_nh >= 0 and i - last_nh == b - 2 and k3[i] < k2[i]:
            tp, bt = nh, ll[i]
        top[i], bot[i] = tp, bt
    ts, bs = pd.Series(top, index=c.index), pd.Series(bot, index=c.index)
    c1 = c.shift(1)
    le = (c > ts) & (c1 <= ts.shift(1))
    lx = (c < bs) & (c1 >= bs.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
