"""EMA 10 / 20 river, broker days: a bar opening and closing above both EMAs goes long, a bar opening and closing below
both goes short; always in once started.
Port of FMZ strategy #432760 "Dual Moving Average Crossover Strategy" (MA River CC v1).

FMZ source id: 432760

Source
    https://www.fmz.com/strategy/432760 (PineScript v3, FMZ last modified 2023-11-21 11:34:09).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 119-156), EMA 10 / EMA 20 of the close
    open > ema10 and open > ema20 and close > ema10 and close > ema20 -> entry long (and close short)
    open < both and close < both -> entry short (and close long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security on the chart's own timeframe adds nothing. The closes of the other side are
      written after the entries and do not undo a reversal (C31-C39 convention), so the strategy
      flips: REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, open and close against two EMAs.
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

NAME = "fmz_432760_ema_river_flip"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [10, 5],
    "ma2": [20, 40],
}
DEFAULT_PARAMS = {"ma1": 10, "ma2": 20}


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
    o, c = bars_df["open"], bars_df["close"]
    e1 = c.ewm(span=int(p["ma1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ma2"]), adjust=False).mean()
    x = ((o > e1) & (o > e2) & (c > e1) & (c > e2)).to_numpy()
    y = ((o < e1) & (o < e2) & (c < e1) & (c < e2)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if x[i]:
            pos = 1
        if y[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
