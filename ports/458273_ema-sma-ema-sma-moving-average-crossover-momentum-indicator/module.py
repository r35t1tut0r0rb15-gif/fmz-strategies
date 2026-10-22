"""EMA 9 crossings of the SMA 30, daily bars, long only: the EMA 9 crossing over the SMA 30 buys; crossing under the SMA 30 or the SMA 50 sells.
Port of FMZ strategy #458273 "EMA-SMA-均线交叉-动量指标-EMA-SMA-Moving-Average-Crossover-Momentum-Indicator" (EMA/SMA Crossover Strategy with Additional MAs).

FMZ source id: 458273

Source
    https://www.fmz.com/strategy/458273 (PineScript v5, FMZ last modified 2024-07-31 14:41:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 195-242), EMA 9; SMA 30 / 50 (200 / 325 plotted only)
    crossover(ema9, sma30) -> entry Buy;  crossunder(ema9, sma30) or crossunder(ema9, sma50) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry is called before the close; the close acts only on a long held into the bar. Long only.
      No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA / SMA crossings.
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

NAME = "fmz_458273_ema9_cross_sma30_exit_sma30_or_50_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [9, 5],
    "sma1": [30, 20],
    "sma2": [50, 100],
}
DEFAULT_PARAMS = {"ema_len": 9, "sma1": 30, "sma2": 50}


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
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    s1, s2 = c.rolling(int(p["sma1"])).mean(), c.rolling(int(p["sma2"])).mean()
    buy = ((e > s1) & (e.shift(1) <= s1.shift(1))).to_numpy()
    sell = (((e < s1) & (e.shift(1) >= s1.shift(1))) | ((e < s2) & (e.shift(1) >= s2.shift(1)))).to_numpy()
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
