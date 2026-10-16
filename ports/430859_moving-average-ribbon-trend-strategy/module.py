"""Noro's trend ribbon, broker days: a close above the previous bar's 20-bar highest SMA 20 of ohlc4 goes long, a close
below its lowest goes short.
Port of FMZ strategy #430859 "Moving Average Ribbon Trend Strategy" (Noro's Trend Ribbon Strategy).

FMZ source id: 430859

Source
    https://www.fmz.com/strategy/430859 (PineScript v4, FMZ last modified 2023-11-02 15:22:17).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 191-219), SMA 20 of ohlc4, channel 20
    ma = sma(ohlc4, 20); h = highest(ma, 20); l = lowest(ma, 20)
    close > h[1] -> entry long;  close < l[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a channel of a moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity per entry stored in original_sizing.txt.
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

NAME = "fmz_430859_noro_trend_ribbon"
FAMILY = "ma_envelope_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10, 40],
}
DEFAULT_PARAMS = {"length": 20}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    ma = ((o + h + lo + c) / 4).rolling(n).mean()
    hh, ll = ma.rolling(n).max().shift(1), ma.rolling(n).min().shift(1)
    up, dn = (c > hh).to_numpy(), (c < ll).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        if dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
