"""Double-smoothed Heikin Ashi colour turns, long only, broker days: the second Heikin Ashi pass (built on the Heikin Ashi
candles) turning green goes long; turning red closes it.
Port of FMZ strategy #432333 "Heikin Ashi Reverse Strategy" (Heikin-Ashi Change Strategy).

FMZ source id: 432333

Source
    https://www.fmz.com/strategy/432333 (PineScript v4, FMZ last modified 2023-11-16 15:44:14).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 305-342), Heikin Ashi candles on (security of the heikinashi ticker, same timeframe)
    ha = Heikin Ashi candles; haclose = (ha.o + ha.h + ha.l + ha.c) / 4; haopen = na(haopen[1]) ? (ha.o + ha.c) / 2 : (haopen[1] + haclose[1]) / 2
    haclose > haopen and haclose[1] <= haopen[1] -> entry long ("long", 1);  haclose <= haopen and haclose[1] > haopen[1] -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The first pass is the chart's own Heikin Ashi candles (security of the heikinashi ticker on the
      same timeframe, no look-ahead): close = ohlc4, open = the average of the previous HA open and
      close (seeded with (open + close) / 2), high / low the extremes with them. The second pass is
      applied to those candles, as written.
    * strategy.entry("long", 1) is a long entry; the short entry is commented out. Long only;
      Opposite entries cannot occur. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle colour turns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432333_double_heikin_ashi_turn_long"
FAMILY = "heikin_ashi_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "passes": [2, 1],
}
DEFAULT_PARAMS = {"passes": 2}


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


def _ha(o, h, lo, c):
    hc = (o + h + lo + c) / 4
    ho = np.full(len(c), np.nan)
    for i in range(len(c)):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 or np.isnan(ho[i - 1]) else (ho[i - 1] + hc[i - 1]) / 2
    hh = np.maximum(h, np.maximum(ho, hc))
    hl = np.minimum(lo, np.minimum(ho, hc))
    return ho, hh, hl, hc


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    for _ in range(int(p["passes"])):
        o, h, lo, c = _ha(o, h, lo, c)
    g = c > o
    g1 = np.concatenate(([False], g[:-1]))
    r1 = np.concatenate(([False], c[:-1] > o[:-1]))
    le = g & ~g1 & (np.arange(len(g)) >= 1)
    lx = ~g & r1
    false = np.zeros(len(g), dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, false, false.copy()))


def portfolio_kwargs(**params):
    return {}
