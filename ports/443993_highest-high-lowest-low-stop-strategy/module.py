"""Three higher closes from flat go long, three lower closes short, daily bars; the stop at the previous 20-bar low (high for shorts), re-sent every bar as the window rolls, is kept pending, so the port
has no exit.
Port of FMZ strategy #443993 "Highest High Lowest Low Stop Strategy" (Highest high/lowest low stop).

FMZ source id: 443993

Source
    https://www.fmz.com/strategy/443993 (PineScript v5, FMZ last modified 2024-03-08 14:32:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 130-177), highest high 20, lowest low 20 (previous bar)
    flat and close > close[1] > close[2] > close[3] -> entry EL;  flat and three lower closes -> entry ES
    long: exit(XL HH, stop = lowest(low, 20)[1]);  short: exit(XS LL, stop = highest(high, 20)[1]) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the previous 20-bar low (high), re-sent on every bar, so it moves with the window
      after entry: stops() cannot express a level re-set every bar, so it is described here and kept
      pending (as #438034, mark trailing_stop_pending). Entries come only from flat, so without the stop
      the port has no exit (as #437800). No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the rolling channel stop described (pending).
    2 generic: PASS, three-close runs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_443993_three_close_run_channel_stop_pending"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
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
    c = bars_df["close"]
    c1, c2, c3 = c.shift(1), c.shift(2), c.shift(3)
    hi = ((c > c1) & (c1 > c2) & (c2 > c3)).to_numpy()
    lw = ((c < c1) & (c1 < c2) & (c2 < c3)).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = 0
    for i in range(m):
        if held == 0 and hi[i]:
            le[i], held = True, 1
        elif held == 0 and lw[i]:
            se[i], held = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
