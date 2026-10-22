"""EMA 5 against the EMA 13, 2-day bars, short only: the EMA 5 under the EMA 13 sells short, the EMA 5 over it covers.
Port of FMZ strategy #451729 "EMA5与EMA13交叉策略-EMA5-and-EMA13-Crossover-Strategy" (5-13 EMA by Naimesh ver04).

FMZ source id: 451729

Source
    https://www.fmz.com/strategy/451729 (PineScript v5, FMZ last modified 2024-05-17 15:28:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-144), EMA 5 / 13; quantity 1; test window 2021-2099 (testPeriod() returns true)
    expo < ma -> entry Short (when);  expo > ma -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both tests are states: the short is (re)entered on every bar with the EMA 5 under the EMA 13
      (ignored while held) and closed on the first bar with it over. testPeriod() returns true, so the
      date inputs only colour the background. The long entry is commented out. Short only: Opposite
      entries cannot occur. The quantity 1 is sizing. FREQ = "2D" from the backtest header (blocks of
      2 broker days, each stamped with its first minute).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA 5 / 13 trend state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity 1 stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only: Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451729_ema5_13_state_short_2d"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 9],
    "slow": [13, 21],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 13}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    false = pd.Series(False, index=bars_df.index)
    return false, false.copy(), f < s, f > s


def portfolio_kwargs(**params):
    return {}
