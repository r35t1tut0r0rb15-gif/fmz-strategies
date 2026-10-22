"""SMA 10 envelope (+- 10 %) re-entries, 2-day bars, long only: the close crossing back over the lower envelope buys from flat; the close crossing over the SMA sells.
Port of FMZ strategy #454743 "Dynamic Channel Percentage Envelope Strategy" (Envelope Strategy).

FMZ source id: 454743

Source
    https://www.fmz.com/strategy/454743 (PineScript v4, FMZ last modified 2024-06-21 15:33:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 164-197), SMA 10 (EMA off); envelope 10 %
    flat and crossover(close, sma x 0.9) -> entry Buy;  long and crossover(close, sma) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * position_size == 1 is the default one-unit long, so the close acts on a held long. A bar that
      crosses both lines while flat only enters (the close finds no trade yet), followed in a small
      loop. Long only. No sizing code. FREQ = "2D" from the backtest header (blocks of 2 broker days,
      each stamped with its first minute).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, envelope re-entries with a basis exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454743_sma10_envelope_reentry_basis_exit_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "pct": [10.0, 5.0],
}
DEFAULT_PARAMS = {"length": 10, "pct": 10.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, 2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    basis = c.rolling(int(p["length"])).mean()
    lower = basis * (1 - float(p["pct"]) / 100)
    c1 = c.shift(1)
    buy = ((c > lower) & (c1 <= lower.shift(1))).to_numpy()
    sell = ((c > basis) & (c1 <= basis.shift(1))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend = 0, 0
    for i in range(m):
        if pend == 1:
            pos = 1
        elif pend == 2:
            pos = 0
        pend = 0
        if buy[i] and pos == 0:
            le[i], pend = True, 1
        if sell[i] and pos == 1:
            lx[i], pend = True, 2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
