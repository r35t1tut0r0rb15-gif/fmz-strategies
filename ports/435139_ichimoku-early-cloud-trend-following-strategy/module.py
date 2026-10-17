"""Ichimoku cloud breakouts with a free Chikou, broker days: a close above the high of 26 bars ago, above the cloud drawn for
26 bars ago and above the cloud drawn for today goes long, closed when the close falls under either span of today's cloud;
the short mirror; positions reverse on the opposite entry.
Port of FMZ strategy #435139 "Ichimoku-Early-Cloud-Trend-Following-Strategy-一云双提前知机会均线趋势跟踪策略" (Ichimoku Cloud Strategy Idea).

FMZ source id: 435139

Source
    https://www.fmz.com/strategy/435139 (PineScript v4, FMZ last modified 2023-12-12 16:11:09).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 173-223), Tenkan 9, Kijun 26, Senkou B 52, displacement 26; long-only off; stop-loss off
    enter_long = close > high[26] and close > max(lead1[52], lead2[52]) and close > max(lead1[26], lead2[26]);  exit_long = close < lead1[26] or close < lead2[26]
    enter_short mirror with low[26] and min(...);  exit_short = close > lead1[26] or close > lead2[26]

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Today's cloud" is the leading spans computed 26 bars ago (the plot offset), read as
      lead[26] in the code: only past bars. The 5 % stop is off by default (not ported). The closes
      act on the position held on the bar; an entry on the same bar wins. strategy.entry reverses:
      REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku spans.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 99 % of equity and commission stored.
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

NAME = "fmz_435139_ichimoku_chikou_free_cloud"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "disp": [26, 13],
    "long_only": [False, True],
}
DEFAULT_PARAMS = {"conv": 9, "base": 26, "span2": 52, "disp": 26, "long_only": False}


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
    don = lambda n: (lo.rolling(n).min() + h.rolling(n).max()) / 2  # noqa: E731
    l1 = (don(int(p["conv"])) + don(int(p["base"]))) / 2
    l2 = don(int(p["span2"]))
    d = int(p["disp"])
    a1, b1 = l1.shift(d), l2.shift(d)
    a2, b2 = l1.shift(2 * d), l2.shift(2 * d)
    el = ((c > h.shift(d)) & (c > np.maximum(a2, b2)) & (c > np.maximum(a1, b1))).to_numpy()
    xl = ((c < a1) | (c < b1)).to_numpy()
    es = ((c < lo.shift(d)) & (c < np.minimum(a2, b2)) & (c < np.minimum(a1, b1))).to_numpy()
    xs = ((c > a1) | (c > b1)).to_numpy()
    lonly = bool(p["long_only"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if pos == 1 and xl[i]:
            new = 0
        if pos == -1 and xs[i] and not lonly:
            new = 0
        if el[i]:
            new = 1
        if es[i] and not lonly:
            new = -1
        tgt[i] = new
        pos = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
