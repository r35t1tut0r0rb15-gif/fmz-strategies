"""Closes under the previous bar's low toggle a long, daily bars: when flat, such a bar goes long; when long, the next such bar closes (the line-breakout block never acts).
Port of FMZ strategy #449518 "Trend Capturing Strategy with Horizontal Line Breakout" (Alarm Trader_ALL (horizontal line breakout)).

FMZ source id: 449518

Source
    https://www.fmz.com/strategy/449518 (PineScript v5, FMZ last modified 2024-04-26 15:22:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-136), line length 20, last 10 lines (the line array is never filled)
    low[1] > close -> (open trades ? close AL : entry AL);  open < lastLinePrice and close > lastLinePrice -> same toggle (the lines array stays empty: never)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line.new / push code is commented out, so the lines array stays empty, lastLinePrice stays
      na and the breakout toggle never fires. The remaining toggle buys a close under the previous
      low when flat and closes the long on the next such bar (opentrades counts the filled long).
      Long only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close-below-prior-low toggle.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449518_close_below_prior_low_toggle_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
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
    lo, c = bars_df["low"], bars_df["close"]
    sig = (lo.shift(1) > c).to_numpy()
    m = len(sig)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if sig[i]:
            if held:
                lx[i] = True
            else:
                le[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
