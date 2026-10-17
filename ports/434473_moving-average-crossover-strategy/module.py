"""EMA 20 / 50 crosses with one-bar trades, broker days, as written: a cross up goes long and a cross down goes short, and
each trade is closed at the open after its first full bar, because both side's brackets apply to every position.
Port of FMZ strategy #434473 "Moving Average Crossover Strategy" (QUANT).

FMZ source id: 434473

Source
    https://www.fmz.com/strategy/434473 (PineScript v5, FMZ last modified 2023-12-06 16:58:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 136-163), EMA 20 / 50; SL 0.4 %, TP 0.7 % of the average price
    crossover(ema20, ema50) -> entry long;  exit "Venta Call" (stop = avg (1 - 0.4 %), limit = avg (1 + 0.7 %))
    crossover(ema50, ema20) -> entry short;  exit "Venta Put" (stop = avg (1 + 0.4 %), limit = avg (1 - 0.7 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both strategy.exit calls have no from_entry, so both apply to whatever position is open, every
      bar. They are armed at the close of the fill bar (the average price is na before); at the next
      open the other side's levels sit on the wrong side of the price (a long's sell stop above it
      and its sell limit below it), so one of them fills at that open. The port therefore closes each
      trade with an exit signal on its fill bar (filled at the next open), unless an opposite cross
      on that bar reverses it. The intended per-side bracket is owed.
    * REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the as-written exits are a next-bar close.
    2 generic: PASS, average crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket quoted in original_sizing.txt.
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

NAME = "fmz_434473_ema_cross_one_bar"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50}


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
    e1 = c.ewm(span=int(p["fast"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = ((e1 > e2) & (e1.shift(1) <= e2.shift(1))).to_numpy()
    se = ((e2 > e1) & (e2.shift(1) <= e1.shift(1))).to_numpy()
    m = len(le)
    lx, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    for i in range(m - 1):
        j = i + 1                       # the fill bar: the brackets are armed at its close
        if le[i] and not se[j]:
            lx[j] = True
        if se[i] and not le[j]:
            sx[j] = True
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
