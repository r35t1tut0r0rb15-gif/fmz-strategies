"""Extreme drawdown buys held a fixed time, daily bars, long only: when the close's drawdown from the 50-bar high is at least one standard deviation (50 bars) below its 50-bar mean, a buy from flat is held 35 bars from its signal bar.
Port of FMZ strategy #473402 "Statistical Deviation Based Market Extreme Drawdown Strategy" (Buy When There's Blood in the Streets Strategy).

FMZ source id: 473402

Source
    https://www.fmz.com/strategy/473402 (PineScript v5, FMZ last modified 2024-11-29 16:46:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-135), lookback 50; stdev length 50; threshold -1.0; exit after 35 bars
    dd = (close - highest(high, 50)) / highest x 100;  dd <= sma(dd, 50) - 1.0 x stdev(dd, 50) and flat -> entry Long, entryBar := bar_index;  long and bar_index - entryBar >= 35 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The hold counts from the signal bar (entryBar is set when the entry is sent), as written; a loop
      follows the position so entries come only from flat. ta.stdev is the population deviation. Long
      only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, drawdown-deviation entries with a time exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473402_drawdown_1sd_below_mean_hold35_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [50, 100],
    "threshold": [-1.0, -2.0],
    "exit_bars": [35, 20],
}
DEFAULT_PARAMS = {"lookback": 50, "threshold": -1.0, "exit_bars": 35, "sd_len": 50}


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
    pk = bars_df["high"].rolling(int(p["lookback"])).max()
    dd = (c - pk) / pk * 100
    n = int(p["sd_len"])
    go = (dd <= dd.rolling(n).mean() + float(p["threshold"]) * dd.rolling(n).std(ddof=0)).to_numpy()
    hold = int(p["exit_bars"])
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, eb = 0, 0, -1
    for i in range(m):
        if pend == 1:
            pos, pend = 1, 0
        elif pend == 2:
            pos, pend = 0, 0
        if go[i] and pos == 0 and pend == 0:
            le[i], pend, eb = True, 1, i
        if pos == 1 and pend == 0 and i - eb >= hold:
            lx[i], pend = True, 2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
