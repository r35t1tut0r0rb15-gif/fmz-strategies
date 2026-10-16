"""Pump and dump bodies, broker days, long only: a green body over 3 times its 100-bar average goes long; a red body over 3
times the average, or a later low under the signal bar's low, closes the long.
Port of FMZ strategy #430280 "Cryptocurrency动量突破策略Cryptocurrency-Momentum-Breakout-Strategy" ([BoTo] Pump&Dump Strategy).

FMZ source id: 430280

Source
    https://www.fmz.com/strategy/430280 (PineScript v3, FMZ last modified 2023-10-26 17:23:20).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 185-216), body SMA 100 x 3, stop 100 %
    pump = |close - open| > 3 sma(|close - open|, 100) and close > open -> entry long
    autostop = low of the pump bar taken when flat; userstop = close - close x 100 % (= 0)
    dump (big red body) or low < autostop or low < userstop -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop tests read the bar's low at its close and close with a market order (next open): an
      exit signal, not a stop order. The 100 % user stop sits at zero: inert.
    * autostop is reset only by a pump while flat (a pump while long keeps the first low). close_all
      acts on the position held at the start of the bar.
    * Long only; Opposite entries cannot occur. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked low exit.
    2 generic: PASS, body ratios.
    3 crypto-exchange-only: no ("Cryptocurrency" in the corpus title only; exchange pair in the header).
    4 signals only: 100 % of equity per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430280_pump_dump_bodies_long"
FAMILY = "momentum_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50],
    "multiplier": [3.0, 2.0],
}
DEFAULT_PARAMS = {"length": 100, "multiplier": 3.0}


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
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    body = (c - o).abs()
    big = body > body.rolling(int(p["length"])).mean() * p["multiplier"]
    pump = (big & (c > o)).to_numpy()
    dump = (big & (c < o)).to_numpy()
    lv = lo.to_numpy(dtype=float)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos, autostop = 0, np.nan
    for i in range(m):
        start = pos
        if pump[i] and start == 0:
            autostop = lv[i]
        if pump[i]:
            pos = 1
        if start != 0 and (dump[i] or lv[i] < autostop):
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
