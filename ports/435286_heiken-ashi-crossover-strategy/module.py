"""Heikin-Ashi colour, broker days: a Heikin-Ashi candle that closes above its open holds a long, one that closes at or below its
open a short (reversing).
Port of FMZ strategy #435286 "Heiken Ashi Crossover Strategy" (Heikin-Ashi Strategy).

FMZ source id: 435286

Source
    https://www.fmz.com/strategy/435286 (PineScript v2, FMZ last modified 2023-12-13 17:46:10).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 182-195), haclose = ohlc4; haopen = the average of the previous haopen and haclose (first bar: (open + close) / 2)
    haclose = (open + high + low + close) / 4;  haopen = na(haopen[1]) ? (open + close) / 2 : (haopen[1] + haclose[1]) / 2
    haclose > haopen -> entry long;  haclose <= haopen -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The candle colour is a state every bar; the signal is sent on the change of colour only. The
      Heikin-Ashi open is a recursion from the first bar, so it carries the start of the series
      (as in Pine). strategy.entry reverses: REVERSAL INTENDED. The From / To date inputs are not
      used by the orders. No parameter is searched (the author gives none). Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle colour.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435286_heikin_ashi_colour"
FAMILY = "candle_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    hac = (o + h + lo + c) / 4
    m = len(hac)
    hao = np.empty(m)
    for i in range(m):
        hao[i] = (o[i] + c[i]) / 2 if i == 0 else (hao[i - 1] + hac[i - 1]) / 2
    up = hac > hao
    prev = np.concatenate(([False], up[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    first = np.zeros(m, dtype=bool)
    first[0] = True
    return (pd.Series(up & (~prev | first), index=ix), false,
            pd.Series(~up & (prev | first), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
