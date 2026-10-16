"""KPL swing on 2-day bars: a trailing line switches between the 20-bar lowest low and highest high
according to the breakout direction before the latest one; the close crossing above the line goes
long, crossing below goes short (always in the market after the first cross).
Port of FMZ strategy #427453 "KPL Swing Trading Strategy".

FMZ source id: 427453

Source
    https://www.fmz.com/strategy/427453 (PineScript v4, FMZ last modified 2023-09-21 11:09:04).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 130-149), length 20
    avd = close > highest(high, 20)[1] ? 1 : close < lowest(low, 20)[1] ? -1 : 0
    avn = valuewhen(avd != 0, avd, 1); tsl = avn == 1 ? lowest(low, 20) : highest(high, 20)
    crossover(close, tsl) -> entry long; crossunder(close, tsl) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * valuewhen(..., 1) is the SECOND most recent breakout direction (occurrence 1), as Pine defines it.
    * 2-day bars are built from broker days (session ends 17:00 America/New_York) in fixed blocks of
      two broker-day dates counted from 1970-01-01, as worker A's #426995 (block phase: decision owed).
    * The `sl` line only plots. strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "2D" from the backtest header (period 2d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bar counts only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427453_kpl_swing"
FAMILY = "donchian_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10, 40],
}
DEFAULT_PARAMS = {"length": 20}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker-day dates counted from 1970-01-01 (as worker A's #426995), each stamped
    with the session start of its first broker day."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def simulate(bars_df, **params):
    n = int({**DEFAULT_PARAMS, **params}["length"])
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    res, sup = h.rolling(n).max(), lo.rolling(n).min()
    avd = np.where(c > res.shift(1), 1, np.where(c < sup.shift(1), -1, 0))
    m = len(c)
    avn = np.zeros(m)
    hits = []
    for i in range(m):
        if avd[i] != 0:
            hits.append(avd[i])
        avn[i] = hits[-2] if len(hits) >= 2 else np.nan        # valuewhen(avd != 0, avd, 1)
    tsl = np.where(avn == 1, sup.to_numpy(), res.to_numpy())
    tsl[np.isnan(avn)] = res.to_numpy()[np.isnan(avn)]       # avn na: the "else" branch (res)
    cv = c.to_numpy(dtype=float)
    c1, t1 = np.concatenate(([np.nan], cv[:-1])), np.concatenate(([np.nan], tsl[:-1]))
    up, dn = (cv > tsl) & (c1 <= t1), (cv < tsl) & (c1 >= t1)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
