"""Seven-day closing lows above the SMA 200, daily bars, long only: a close at the 7-bar closing low while over the SMA 200 buys; a close at the 7-bar closing high sells.
Port of FMZ strategy #473246 "Double Seven Strategy Trend Following and Mean Reversion Dual Optimization Trading SystemDouble Seven Strategy" (Larry Connors' Double Seven Strategy).

FMZ source id: 473246

Source
    https://www.fmz.com/strategy/473246 (PineScript v5, FMZ last modified 2024-11-28 15:41:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-119), SMA 200; lowest / highest close over 7 bars (current bar included)
    close > sma200 and close <= lowest(close, 7) -> entry Long;  close >= highest(close, 7) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The windows include the current close, so the tests mean a new 7-bar closing low / high. The entry
      and exit tests cannot hold together (except on a flat 7-bar window, where the entry, called first,
      opens from flat and the close acts only on a held long). Long only. No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, 7-day closing extremes in an uptrend.
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

NAME = "fmz_473246_connors_double_seven_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "window": [7, 5],
    "ma_len": [200, 100],
}
DEFAULT_PARAMS = {"window": 7, "ma_len": 200}


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
    w = int(p["window"])
    buy = ((c > c.rolling(int(p["ma_len"])).mean()) & (c <= c.rolling(w).min())).to_numpy()
    sell = (c >= c.rolling(w).max()).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if buy[i] and pos == 0:
            le[i], pos = True, 1
        elif sell[i] and pos == 1:
            lx[i], pos = True, 0                 # the close acts only on a long held into the bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
