"""Long-horizon Donchian highs, daily bars, long only: a high at the 260-bar high with a close above one of the last three closes whose bar was also at its 260-bar high goes long; a low at the 60-bar low
with a lower close than the previous bar, which was also at its 60-bar low, closes.
Port of FMZ strategy #442936 "Donchain Channel Based Trading Strategy" (Donchain channel strategy).

FMZ source id: 442936

Source
    https://www.fmz.com/strategy/442936 (PineScript v5, FMZ last modified 2024-02-27 14:57:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 129-234), daily: entry window 52 x 5 = 260, exit window 12 x 5 = 60; KAMA 21 (plot only); close_all two days before the run date
    entry: for i = 1..3: high >= highest(260) and close > close[i] and high[i] >= highest(260)[i] -> first i -> entry Buy
    exit (the loop breaks after i = 1): low <= lowest(60) and close < close[1] and low[1] <= lowest(60)[1] -> close_all;  date(timenow) - 2 days -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * On a daily chart the windows are 260 and 60 bars, as written. ta.highest / ta.lowest with one
      argument use the high / low. The exit loop breaks after its first pass, so only i = 1 is tested,
      as written. The close-all keyed to the wall-clock date (timenow) depends on the day the script is
      run, not on the data, and is dropped. The KAMA only plots. Long only. No sizing code. FREQ = "1D"
      from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, long-window channel highs with a short-window exit.
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

NAME = "fmz_442936_donchian_260_high_60_low_exit_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "longer": [260, 120],
    "shorter": [60, 20],
}
DEFAULT_PARAMS = {"longer": 260, "shorter": 60}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hl = h.rolling(int(p["longer"])).max()
    ls = lo.rolling(int(p["shorter"])).min()
    at_h = h >= hl
    go = pd.Series(False, index=c.index)
    for k in (1, 2, 3):
        go |= at_h & (c > c.shift(k)) & at_h.shift(k, fill_value=False)
    at_l = lo <= ls
    out = at_l & (c < c.shift(1)) & at_l.shift(1, fill_value=False)
    gv, ov_ = go.to_numpy(), out.to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if gv[i] and not held:
            le[i] = True
        elif ov_[i] and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
