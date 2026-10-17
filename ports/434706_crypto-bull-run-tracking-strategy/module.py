"""TEMA 210 / DEMA 230 crosses, broker days: the TEMA crossing above the DEMA goes long, crossing below goes short; each cross
also closes the opposite side, so the position reverses.
Port of FMZ strategy #434706 "Crypto Bull Run Tracking Strategy" (Crypto Bull Run Tracker).

FMZ source id: 434706

Source
    https://www.fmz.com/strategy/434706 (PineScript v5, FMZ last modified 2023-12-08 15:45:47).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 207-250), DEMA 230, TEMA 210 on close; bar delay 5 (unused)
    crossunder(tema, dema) and long -> close long;  crossover(tema, dema) and short -> close short
    crossover(tema, dema) -> entry long;  crossunder(tema, dema) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes and the entries share the same crosses, so the position simply reverses. The bar
      delay is recorded but never used. strategy.entry reverses: REVERSAL INTENDED. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crosses.
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

NAME = "fmz_434706_tema_dema_cross"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dema_len": [230, 100],
    "tema_len": [210, 90],
}
DEFAULT_PARAMS = {"dema_len": 230, "tema_len": 210}


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
    ema = lambda x, n: x.ewm(span=n, adjust=False).mean()  # noqa: E731
    nd, nt = int(p["dema_len"]), int(p["tema_len"])
    e1 = ema(c, nd)
    dema = 2 * e1 - ema(e1, nd)
    t1 = ema(c, nt)
    t2 = ema(t1, nt)
    tema = 3 * (t1 - t2) + ema(t2, nt)
    le = ((tema > dema) & (tema.shift(1) <= dema.shift(1))).astype(bool)
    se = ((tema < dema) & (tema.shift(1) >= dema.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
