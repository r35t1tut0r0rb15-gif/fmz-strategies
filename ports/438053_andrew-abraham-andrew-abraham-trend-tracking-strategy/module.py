"""Andrew Abraham's trend trader, broker days: a line at the previous 21-bar high minus 3 x the 21-bar WMA of the true range (or the previous low plus it) follows the close; a close above the line holds a
long, below it a short; reversing.
Port of FMZ strategy #438053 "Andrew-Abraham趋势追踪策略Andrew-Abraham-Trend-Tracking-Strategy" (Trend Trader Strategy).

FMZ source id: 438053

Source
    https://www.fmz.com/strategy/438053 (PineScript v2, FMZ last modified 2024-01-08 16:21:11).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 127-144), Length 21, Multiplier 3, reverse off
    avgTR = wma(atr(1), 21);  hiLimit = highest(21)[1] - 3 avgTR[1];  loLimit = lowest(21)[1] + 3 avgTR[1]
    ret = hiLimit if close above both, loLimit if close below both, else ret[1] (nz 0);  pos = 1 if close > ret, -1 if close < ret, else pos[1];  entries by pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * atr(1) is the true range. highest / lowest are of the highs / lows. The state is a level, so the
      entry is sent on every bar of the state; pos 0 sends nothing. reverse is off. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel line from extremes and average true range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND434966 (2 members, best partner #434966, Jaccard 0.705); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438053_abraham_trend_trader"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 14],
    "mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"length": 21, "mult": 3.0, "reverse": False}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    avg_tr = _wma(tr, n)
    k = float(p["mult"])
    hi_lim = (h.rolling(n).max().shift(1) - avg_tr.shift(1) * k).to_numpy()
    lo_lim = (lo.rolling(n).min().shift(1) + avg_tr.shift(1) * k).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ret, st = 0.0, np.zeros(m)
    for i in range(m):
        x = cv[i]
        if x > hi_lim[i] and x > lo_lim[i]:
            ret = hi_lim[i]
        elif x < lo_lim[i] and x < hi_lim[i]:
            ret = lo_lim[i]
        prev = st[i - 1] if i > 0 else 0.0
        st[i] = 1.0 if x > ret else (-1.0 if x < ret else prev)
    if p["reverse"]:
        st = -st
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(st == 1, index=ix), false, pd.Series(st == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
