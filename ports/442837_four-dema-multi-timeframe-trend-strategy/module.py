"""Four DEMAs (10 / 15 / 21 / 30) fully ordered, daily bars: all four stacked upward goes long, downward goes short; any crossing of the DEMA 10 and DEMA 15 closes; reversing.
Port of FMZ strategy #442837 "Four DEMA Multi Timeframe Trend Strategy" (dema10-15-21-30 (4dema)).

FMZ source id: 442837

Source
    https://www.fmz.com/strategy/442837 (PineScript v3, FMZ last modified 2024-02-26 14:14:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 137-192), DEMA 10 / 15 / 21 / 30 on the close
    long = dema1 > dema2 > dema3 > dema4 (all pairs) -> entry Long;  cross(dema1, dema2) -> close Long;  short = the reverse order -> entry Short;  cross(dema1, dema2) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * cross() fires on a crossing in either direction. Ported in call order with one position at a
      time: a close acts only on a held position, and a close after a reversing entry leaves the
      reversal standing. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, DEMA ordering with a cross exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442837_four_dema_order_cross_exit_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short": [10, 5],
    "long3": [30, 50],
}
DEFAULT_PARAMS = {"short": 10, "long": 15, "long2": 21, "long3": 30}


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


def _dema(c, n):
    e1 = c.ewm(span=n, adjust=False).mean()
    return 2 * e1 - e1.ewm(span=n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d1, d2, d3, d4 = (_dema(c, int(p[k])) for k in ("short", "long", "long2", "long3"))
    lg = ((d1 > d2) & (d1 > d3) & (d1 > d4) & (d2 > d3) & (d2 > d4) & (d3 > d4)).to_numpy()
    sh = ((d4 > d3) & (d4 > d2) & (d4 > d1) & (d3 > d2) & (d3 > d1) & (d2 > d1)).to_numpy()
    x = (((d1 > d2) & (d1.shift(1) <= d2.shift(1))) | ((d1 < d2) & (d1.shift(1) >= d2.shift(1)))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if lg[i] and new != 1:
            new = 1
        if x[i] and held == 1 and new == 1:
            new = 0
        if sh[i] and new != -1:
            new = -1
        if x[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
