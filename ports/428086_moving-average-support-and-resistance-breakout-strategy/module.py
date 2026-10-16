"""LunaOwl support / resistance, broker days: at every cross of the close and SMA 50 the 50-bar high and
low are noted; resistance and support are the values from the cross before the latest one. The close
crossing above resistance goes long, crossing below support goes short.
Port of FMZ strategy #428086 "Moving Average Support and Resistance Breakout Strategy".

FMZ source id: 428086

Source
    https://www.fmz.com/strategy/428086 (PineScript v4, FMZ last modified 2023-09-28 15:20:47).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 147-195), look-back 50
    R = valuewhen(cross(sma50, close), highest(high, 50), 1); S = valuewhen(cross(close, sma50), lowest(low, 50), 1)
    crossover(close, R) -> entry long; crossunder(close, S) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * cross() is either direction, so R and S come from the same cross events; occurrence 1 is the
      cross before the most recent one (Pine valuewhen).
    * strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel levels only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, slippage and commission stored in original_sizing.txt.
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

NAME = "fmz_428086_lunaowl_sr_breakout"
FAMILY = "channel_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lb": [50, 20, 100, 30],
}
DEFAULT_PARAMS = {"lb": 50}


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


def _valuewhen(cond, src, occ):
    out = np.full(len(src), np.nan)
    hits = []
    for i in range(len(src)):
        if cond[i]:
            hits.append(src[i])
        if len(hits) > occ:
            out[i] = hits[-1 - occ]
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["lb"])
    sma = c.rolling(n).mean()
    d = c - sma
    cross = ((d > 0) & (d.shift(1) <= 0)) | ((d < 0) & (d.shift(1) >= 0))
    cv = cross.to_numpy()
    r = pd.Series(_valuewhen(cv, h.rolling(n).max().to_numpy(), 1), index=c.index)
    s = pd.Series(_valuewhen(cv, lo.rolling(n).min().to_numpy(), 1), index=c.index)
    up = ((c > r) & (c.shift(1) <= r.shift(1))).to_numpy()
    dn = ((c < s) & (c.shift(1) >= s.shift(1))).to_numpy()
    m = len(up)
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
