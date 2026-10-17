"""Rob Booker reversal tabs, broker days: MACD (12 / 26 / 9) crossing above zero while the slow stochastic (70, smoothed
30) is under 30 goes long; crossing below zero with the stochastic over 70 goes short.
Port of FMZ strategy #431971 "Dual Reversal Entry Strategy" (RB Reversal Tabs Strategy).

FMZ source id: 431971

Source
    https://www.fmz.com/strategy/431971 (PineScript v5, FMZ last modified 2023-11-13 17:56:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 193-231), MACD 12 / 26 / 9, stochastic 70 / 30 / 30, levels 30 / 70
    full_k = sma(100 (close - lowest(low, 70)) / (highest(high, 70) - lowest(low, 70)), 30)
    crossover(macd, 0) and full_k < 30 -> entry long;  crossunder(macd, 0) and full_k > 70 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Strategy mode on (the default). strategy.entry reverses: REVERSAL INTENDED. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD sign and stochastic levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431971_rb_reversal_tabs"
FAMILY = "macd_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stoch_period": [70, 35],
    "k_period": [30, 15],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "stoch_period": 70, "k_period": 30, "ob": 70, "os": 30}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    n = int(p["stoch_period"])
    fk = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min()).replace(0.0, np.nan)
    k = fk.rolling(int(p["k_period"])).mean()
    lg = ((macd > 0) & (macd.shift(1) <= 0) & (k < p["os"])).astype(bool)
    sh = ((macd < 0) & (macd.shift(1) >= 0) & (k > p["ob"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def portfolio_kwargs(**params):
    return {}
