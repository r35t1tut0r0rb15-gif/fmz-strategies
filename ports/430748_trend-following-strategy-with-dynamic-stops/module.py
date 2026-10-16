"""UT Bot ATR trailing line, broker days: the close crossing above its 1 x ATR 10 trailing line goes long, crossing below it
goes short.
Port of FMZ strategy #430748 "Trend Following Strategy with Dynamic Stops" (UT Bot Strategy).

FMZ source id: 430748

Source
    https://www.fmz.com/strategy/430748 (PineScript v4, FMZ last modified 2023-11-01 13:46:28).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 229-271), key value 1, ATR 10, Heikin Ashi off
    trail = src > trail[1] and src[1] > trail[1] ? max(trail[1], src - 1 atr) :
            src < trail[1] and src[1] < trail[1] ? min(trail[1], src + 1 atr) : src > trail[1] ? src - 1 atr : src + 1 atr
    buy = src > trail and crossover(ema(src, 1), trail) -> entry long;  sell mirrored -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Heikin Ashi signals are off (src = close); ema(src, 1) is the close. ATR is Wilder's (ta.atr).
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR trailing line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND428704 (2 members, best partner #428704, Jaccard 0.727); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430748_ut_bot_atr_trail"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key": [1.0, 2.0],
    "atr_period": [10, 20],
}
DEFAULT_PARAMS = {"key": 1.0, "atr_period": 10}


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


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    src = bars_df["close"].to_numpy(dtype=float)
    nloss = (float(p["key"]) * _atr(bars_df, int(p["atr_period"]))).to_numpy()
    m = len(src)
    trail = np.zeros(m)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        t1 = trail[i - 1] if i > 0 else 0.0
        s1 = src[i - 1] if i > 0 else np.nan
        if src[i] > t1 and s1 > t1:
            trail[i] = max(t1, src[i] - nloss[i])
        elif src[i] < t1 and s1 < t1:
            trail[i] = min(t1, src[i] + nloss[i])
        else:
            trail[i] = src[i] - nloss[i] if src[i] > t1 else src[i] + nloss[i]
        if i > 0:
            above = src[i] > trail[i] and s1 <= trail[i - 1]
            below = src[i] < trail[i] and s1 >= trail[i - 1]
            if above:
                pos = 1
            elif below:
                pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
