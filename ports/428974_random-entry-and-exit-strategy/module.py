"""Random entries and exits, long only, broker days: from flat, each bar has a 10 % chance to go long; while
long, each bar has a 3 % chance to close.
Port of FMZ strategy #428974 "Random Entry and Exit Strategy" (Random Entries Work).

FMZ source id: 428974

Source
    https://www.fmz.com/strategy/428974 (PineScript v4, FMZ last modified 2023-10-11 15:17:28).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 211-238), Long Only, enter 10 %, exit 3 %
    r = random(0, 100); enter = 10 > r; exit = 3 > r; direction = random(0, 100) >= 50
    flat and enter (Long Only) -> entry long; exit -> close long   (shorts only for "Short Only" / "Random")

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's random() is unseeded, so the source has no reproducible trade list. The port draws from
      numpy's default generator with a declared `seed` (two draws per bar, r then direction, in bar
      order from the first bar of the data): reproducible, and a faithful model of the same rule. It is
      a random-entry benchmark, ported as written.
    * The same r feeds enter and exit: when flat, r < 3 enters (the close finds no position).
    * The backtest header's args choose "Random" (v_input_1 = 2); the input default is Long Only, which
      is ported (inputs are the input defaults). Start year 2020 is the author's window: dropped.
    * Long only. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; a seeded draw per bar.
    2 generic: PASS, no price units.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428974_random_entries_long"
FAMILY = "random_benchmark"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "seed": [1, 2],
    "exit_frequency": [3, 1],
}
DEFAULT_PARAMS = {"seed": 1, "enter_frequency": 10, "exit_frequency": 3}


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
    m = len(bars_df)
    draws = np.random.default_rng(int(p["seed"])).random((m, 2)) * 100   # r, direction per bar
    r = draws[:, 0]
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if not held and p["enter_frequency"] > r[i]:
            le[i], held = True, True
        elif held and p["exit_frequency"] > r[i]:
            lx[i], held = True, False
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
