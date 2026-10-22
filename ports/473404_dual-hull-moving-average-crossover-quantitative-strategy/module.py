"""HMA 9 / 16 crossings, 2-day bars: the cross up goes long, the cross down goes short; reversing.
Port of FMZ strategy #473404 "Dual Hull Moving Average Crossover Quantitative Strategy" (Hull Moving Average Crossover).

FMZ source id: 473404

Source
    https://www.fmz.com/strategy/473404 (PineScript v5, FMZ last modified 2024-11-29 16:53:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 84-119), HMA 9 / 16 (a local hma function)
    hma(src, n) = wma(2 x wma(src, n / 2) - wma(src, n), floor(sqrt(n)));  crossover(fast, slow) -> entry Long;  crossunder -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * n / 2 is read as its floor (WMA lengths are whole bars), as Pine's ta.hma. There is no exit:
      positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "2D" from the
      backtest header (blocks of 2 broker days, as #429148).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Hull MA crossings.
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

NAME = "fmz_473404_hma9_16_cross_reversal"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [16, 30],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 16, "days": 2}


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
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def _wma(x, n):
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _hma(x, n):
    return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(np.floor(np.sqrt(n))))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a, b = _hma(c, int(p["fast"])), _hma(c, int(p["slow"]))
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
