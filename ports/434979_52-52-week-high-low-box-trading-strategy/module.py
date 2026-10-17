"""Darvas boxes from daily values on 1-hour bars, as written: the daily high / low / close (the last completed broker day's)
are sampled on every hourly bar; a box top is a new high of that series over 5 bars confirmed 3 bars later, its bottom the
5-bar low; the daily close crossing above the top goes long, crossing below the bottom goes short (reversing).
Port of FMZ strategy #434979 "52周高低盒子交易策略52-Week-High-Low-Box-Trading-Strategy" (Darvas Box Strategy).

FMZ source id: 434979

Source
    https://www.fmz.com/strategy/434979 (PineScript v4, FMZ last modified 2023-12-11 14:43:30).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 161-187), box length 5; security('D', high / low / close / open)
    LL = lowest(D_Low, 5);  k1 = highest(D_High, 5);  NH = valuewhen(D_High > k1[1], D_High, 0);  box1 = highest(D_High, 3) < highest(D_High, 4)
    TopBox = valuewhen(barssince(D_High > k1[1]) == 3 and box1, NH, 0);  BottomBox = same with LL;  crossover(D_Close, TopBox) -> entry long;  crossunder(D_Close, BottomBox) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * security('D', x) without lookahead is read as the last completed broker day (17:00
      America/New_York), as #429502, built from the port's own bars. The box windows then run on
      the hourly series of those daily values (5 hourly bars, not 5 days), as written.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days.
    2 generic: PASS, box levels from prior-day ranges.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily values on broker days (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434979_darvas_daily_box_hourly"
FAMILY = "channel_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
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


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _prev_day(bars_df):
    day = broker_day(bars_df.index)
    g = pd.DataFrame({k: bars_df[k].to_numpy() for k in ("high", "low", "close")}, index=day)
    d = g.groupby(level=0).agg({"high": "max", "low": "min", "close": "last"}).shift(1)
    return tuple(pd.Series(d[k].reindex(day).to_numpy(), index=bars_df.index) for k in ("high", "low", "close"))


def _vw0(cond, x):
    out = np.full(len(x), np.nan)
    last = np.nan
    for t in range(len(x)):
        if cond[t]:
            last = x[t]
        out[t] = last
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    dh, dl, dc = _prev_day(bars_df)
    b = int(p["boxp"])
    ll = dl.rolling(b).min()
    k1 = dh.rolling(b).max()
    box1 = (dh.rolling(b - 2).max() < dh.rolling(b - 1).max()).to_numpy()
    newh = (dh > k1.shift(1)).to_numpy()
    nh = _vw0(newh, dh.to_numpy())
    m = len(nh)
    since = np.full(m, np.nan)
    last = -1
    for t in range(m):
        if newh[t]:
            last = t
        if last >= 0:
            since[t] = t - last
    cond = (since == b - 2) & box1
    top = _vw0(cond, nh)
    bot = _vw0(cond, ll.to_numpy())
    dcv = dc.to_numpy()
    d1 = np.concatenate(([np.nan], dcv[:-1]))
    t1 = np.concatenate(([np.nan], top[:-1]))
    b1 = np.concatenate(([np.nan], bot[:-1]))
    with np.errstate(invalid="ignore"):
        le = (dcv > top) & (d1 <= t1)
        se = (dcv < bot) & (d1 >= b1)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le & ~se, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
