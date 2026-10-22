"""Exponential Hull MA (EHMA 200) against its value two bars back, daily bars: the EHMA crossing over its 2-bar-old value goes long, crossing under goes short; reversing.
Port of FMZ strategy #445823 "Hull Moving Average Crossover Strategy" (RKTD BETA - Hull Suite by InSilico).

FMZ source id: 445823

Source
    https://www.fmz.com/strategy/445823 (PineScript v4, FMZ last modified 2024-03-22 14:57:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 157-230), source close; variation Ehma; length 200 x 1.0; higher time frame off
    EHMA = ema(2 ema(close, 100) - ema(close, 200), round(sqrt(200)));  crossover(HULL, HULL[2]) -> entry Buy;  crossunder(HULL, HULL[2]) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default variation is Ehma: ema(2 x ema(src, length / 2) - ema(src, length), round(sqrt(length)))
      with length 200 (sqrt rounds to 14). The higher-time-frame option is off, so HULL is the chart's.
      The alert texts name BTC / USDT but are only messages. strategy.entry reverses: REVERSAL INTENDED.
      No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Hull MA slope crossings.
    3 crypto-exchange-only: no (exchange pair in the header only; the alert JSON names BTC / USDT as text only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_445823_ehma200_vs_2bar_cross_reversal"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [200, 55],
}
DEFAULT_PARAMS = {"length": 200}


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


def _ema(x, n):
    return x.ewm(span=int(n), adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    hull = _ema(2 * _ema(c, n // 2) - _ema(c, n), int(round(np.sqrt(n))))
    h2 = hull.shift(2)
    le = (hull > h2) & (hull.shift(1) <= h2.shift(1))
    se = (hull < h2) & (hull.shift(1) >= h2.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
