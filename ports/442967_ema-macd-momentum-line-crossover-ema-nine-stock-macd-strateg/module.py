"""EMA 9 / 30 crossings with a 20-bar deviation filter, daily bars: the EMA 9 crossing over the EMA 30 while the deviation rises goes long, crossing under while it falls goes short; reversing.
Port of FMZ strategy #442967 "动量均线交叉EMA九股MACD策略Momentum-Line-Crossover-EMA-Nine-Stock-MACD-Strategy" (emabb (emabb_collab)).

FMZ source id: 442967

Source
    https://www.fmz.com/strategy/442967 (PineScript v5, FMZ last modified 2024-02-27 16:49:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 130-195), EMA 3 / 9 / 30; MACD 12 / 26 / 9 and BB 20 / 2 (plots only)
    crossover(ema9, ema30) and stdev(close, 20) > stdev[1] -> entry Long;  crossover(ema30, ema9) and stdev < stdev[1] -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bands, the EMA 3 and the MACD only plot. Pine's stdev is the population deviation.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with a volatility filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442967_ema9_30_cross_rising_deviation_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [30, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 30, "dev_len": 20}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    sd = c.rolling(int(p["dev_len"])).std(ddof=0)
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (sd > sd.shift(1))
    se = (s > f) & (s.shift(1) <= f.shift(1)) & (sd < sd.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
