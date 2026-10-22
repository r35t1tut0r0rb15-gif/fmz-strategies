"""Noro's double price-channel trend with pullback bars, broker days: in an up trend (lows above the 21-bar and 5-bar close-channel centres), two red bars with the low under the 5-bar centre go long; the
mirror goes short; reversing.
Port of FMZ strategy #439837 "Dual Moving Average Trend Tracking Strategy" (Noro's Trend MAs Strategy v1.8).

FMZ source id: 439837

Source
    https://www.fmz.com/strategy/439837 (PineScript v2, FMZ last modified 2024-01-24 11:28:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 174-250), long and short on; stops off (5 %); ohlc4 off; fast MA filter on; fast 5, slow 21; bars 2
    trend1 = low > center and low[1] > center[1] ? 1 : high < center and high[1] < center[1] ? -1 : trend1[1];  trend2 = same on center2 : trend1[1];  trend = trend1 == 1 and trend2 == 1 ? 1 : trend2 == -1 ? -1 : trend[1]
    up = trend == 1 and low < center2 and two red bars;  dn = trend == -1 and high > center2 and two green bars;  entry Long on up, entry Short on dn;  stops off (na)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The centres are the middles of the highest and lowest closes over 21 and 5 bars. trend2 falls back
      to trend1[1] and the short test repeats trend2 == -1, both as written. The states start undefined
      (no nz), so nothing trades until they are set. With stops off the stop level stays na and no stop
      is placed. strategy.entry reverses: REVERSAL INTENDED. The 100 % of equity size is sizing. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price-channel centres and bar colours.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and the stop input stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427506 (4 members, best partner #440559, Jaccard 0.714); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439837_noro_trend_mas_v18_pullback"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slowlen": [21, 50],
    "fastlen": [5, 10],
}
DEFAULT_PARAMS = {"slowlen": 21, "fastlen": 5}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    cen = ((c.rolling(int(p["slowlen"])).max() + c.rolling(int(p["slowlen"])).min()) / 2).to_numpy()
    cen2 = ((c.rolling(int(p["fastlen"])).max() + c.rolling(int(p["fastlen"])).min()) / 2).to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    bar = np.sign((c - o).to_numpy(dtype=float))
    m = len(hv)
    t1, t2, t = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    for i in range(1, m):
        p1 = t1[i - 1]
        if lv[i] > cen[i] and lv[i - 1] > cen[i - 1]:
            t1[i] = 1
        elif hv[i] < cen[i] and hv[i - 1] < cen[i - 1]:
            t1[i] = -1
        else:
            t1[i] = p1
        if lv[i] > cen2[i] and lv[i - 1] > cen2[i - 1]:
            t2[i] = 1
        elif hv[i] < cen2[i] and hv[i - 1] < cen2[i - 1]:
            t2[i] = -1
        else:
            t2[i] = p1                                    # falls back to trend1[1], as written
        if t1[i] == 1 and t2[i] == 1:
            t[i] = 1
        elif t2[i] == -1:
            t[i] = -1
        else:
            t[i] = t[i - 1]
    red2 = (bar == -1) & (np.concatenate(([0], bar[:-1])) == -1)
    green2 = (bar == 1) & (np.concatenate(([0], bar[:-1])) == 1)
    up = (t == 1) & (lv < cen2) & red2
    dn = (t == -1) & (hv > cen2) & green2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(up, index=ix), false, pd.Series(dn, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
