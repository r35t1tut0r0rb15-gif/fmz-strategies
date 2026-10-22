"""Percentage bands around a Hull 9, 5-day bars, long only: the close crossing over the 6 % or 3 % lower band goes long; the close crossing over the 3 % or 6 % upper band (or the 3 % lower band again)
closes.
Port of FMZ strategy #443243 "基于HullMA百分比带的量化交易策略Quant-Trading-Strategy-Based-on-HullMA-Percentage-Bands" (hullma percentage lines).

FMZ source id: 443243

Source
    https://www.fmz.com/strategy/443243 (PineScript v3, FMZ last modified 2024-03-01 12:16:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 151-211), Hull 9 on the close; bands +-3 % and +-6 %
    xL1 / xL3 = hull x 1.03 / 1.06;  xL2 / xL4 = hull x 0.97 / 0.94;  crossover(close, xL4) or crossover(close, xL2) -> entry l1
    crossover(close, xL1), crossover(close, xL2), crossover(close, xL3) -> close l1 (strategy.long passed as the when argument, true)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The xL2 crossing both enters and closes: from flat the entry is sent first and the close acts only
      on a held long, so it enters; while long it closes, as written. length / 2 is the integer 4. The
      5-day bars are blocks of five broker days counted from 1970-01-01, each stamped with its first
      minute. Long only. No sizing code. FREQ = "5D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Hull percentage bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker days (17:00 America/New_York, DST by the zone), in blocks of five.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443243_hull9_percent_band_cross_long_5d"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5D"  # backtest header period: 5d (blocks of 5 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [9, 20],
    "band1": [3.0, 2.0],
}
DEFAULT_PARAMS = {"length": 9, "band1": 3.0}

DAYS = 5


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
    return _multiday(raw_1m_df, DAYS)


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    hull = _wma(2 * _wma(c, n // 2) - _wma(c, n), int(np.floor(np.sqrt(n) + 0.5)))
    b1 = float(p["band1"])
    x1, x2 = hull * (1 + b1 / 100), hull * (1 - b1 / 100)
    x3, x4 = hull * (1 + 2 * b1 / 100), hull * (1 - 2 * b1 / 100)

    def xo(a):
        return ((c > a) & (c.shift(1) <= a.shift(1))).to_numpy()

    go = xo(x4) | xo(x2)
    out = xo(x1) | xo(x2) | xo(x3)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if go[i] and not held:
            le[i] = True
        elif out[i] and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
