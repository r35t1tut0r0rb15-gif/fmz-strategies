"""MACD histogram two-bar trends, broker days: a histogram that rose (or held) on each of the last two bars holds a long, one that fell (or held) holds a short; reversing; the entry is sent on every bar of the
state.
Port of FMZ strategy #439978 "基于MACD指标的Histogram进行交易决策策略This-strategy-makes-trading-decisions-based-on-the-trend-of-MACD-Histogram" (Histogram Trends Strategy by Sedkur).

FMZ source id: 439978

Source
    https://www.fmz.com/strategy/439978 (PineScript v4, FMZ last modified 2024-01-25 14:31:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 161-220), year from 2017; MACD 12 / 26 / 9 (EMA); histogram trend number 1
    bull counts i = 0 .. 1 with hist[i + 1] <= hist[i];  bullish = both;  bear counts hist[j + 1] >= hist[j];  bearish = both;  entry buy when bullish, entry sell when bearish (year >= 2017)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With trend number 1 the loops test the last two steps. A flat histogram meets both tests and the
      later sell wins (as #437773). The year test passes on the data. A same-side entry while in the
      position is ignored. strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram steps.
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

NAME = "fmz_439978_sedkur_macd_histogram_trend_state"
FAMILY = "macd_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hist_length": [1, 2],
    "fast_length": [12, 8],
}
DEFAULT_PARAMS = {"hist_length": 1, "fast_length": 12, "slow_length": 26, "signal_length": 9}


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
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast_length"]), adjust=False).mean() - c.ewm(span=int(p["slow_length"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["signal_length"]), adjust=False).mean()
    k = int(p["hist_length"])
    bull = pd.Series(True, index=c.index)
    bear = pd.Series(True, index=c.index)
    for i in range(k + 1):
        bull &= hist.shift(i + 1) <= hist.shift(i)
        bear &= hist.shift(i + 1) >= hist.shift(i)
    bl, br = bull.to_numpy(), bear.to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if br[i]:
            pos = -1
        elif bl[i]:
            pos = 1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
