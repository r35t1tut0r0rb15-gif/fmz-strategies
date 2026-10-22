"""SMA 8 / 21 difference against Bollinger bands of itself, daily bars: the difference crossing back over its lower band (40, 2) goes long, back under its upper band goes short; reversing.
Port of FMZ strategy #443118 "基于MACD和布林带的Momentum-Trend策略Momentum-Trend-Strategy-Based-on-MACD-and-Bollinger-Bands" (Strategy MACD vs BB).

FMZ source id: 443118

Source
    https://www.fmz.com/strategy/443118 (PineScript v4, FMZ last modified 2024-02-29 13:49:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 147-188), SMA 8 / 21 (type 1 = SMA); BB 40 / 2 on the difference
    macd = sma8 - sma21;  lower / upper = sma(macd, 40) -+ 2 stdev(macd, 40);  crossover(macd, lower) -> entry Long;  crossunder(macd, upper) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's stdev is the population deviation. strategy.entry reverses: REVERSAL INTENDED. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA difference against its own bands.
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

NAME = "fmz_443118_ma_diff_own_band_reentry_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [40, 20],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 40, "mult": 2.0, "fast": 8, "slow": 21}


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
    macd = c.rolling(int(p["fast"])).mean() - c.rolling(int(p["slow"])).mean()
    n = int(p["length"])
    basis = macd.rolling(n).mean()
    dev = float(p["mult"]) * macd.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    le = (macd > dn) & (macd.shift(1) <= dn.shift(1))
    se = (macd < up) & (macd.shift(1) >= up.shift(1))
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
