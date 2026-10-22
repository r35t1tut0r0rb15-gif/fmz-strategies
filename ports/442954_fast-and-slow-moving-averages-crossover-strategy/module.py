"""EMA 25 / 62 momentum, daily bars, long only: the EMA 25 turning to at or above the EMA 62 goes long, turning below closes.
Port of FMZ strategy #442954 "Fast and Slow Moving Averages Crossover Strategy" (Fast v Slow Moving Averages Strategy).

FMZ source id: 442954

Source
    https://www.fmz.com/strategy/442954 (PineScript v5, FMZ last modified 2024-02-27 16:06:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 177-249), EMA 25 / 62 (MA type EMA); 100 % of equity, capital 100, commission 0.1; dates (inDateRange true)
    maMomentum = ema25 >= ema62 ? 1 : -1;  crossover(maMomentum, 0) -> entry long;  crossunder(maMomentum, 0) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The momentum state is +1 / -1, so its zero crossings are the changes of the EMA order. Long only.
      The 100 % of equity size, capital and commission are sizing. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA order changes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
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

NAME = "fmz_442954_ema25_62_momentum_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_bars": [25, 10],
    "slow_bars": [62, 100],
}
DEFAULT_PARAMS = {"fast_bars": 25, "slow_bars": 62}


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
    f = c.ewm(span=int(p["fast_bars"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow_bars"]), adjust=False).mean()
    mom = pd.Series(np.where(f >= s, 1, -1), index=c.index)
    le = (mom > 0) & (mom.shift(1) <= 0)
    lx = (mom < 0) & (mom.shift(1) >= 0)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
