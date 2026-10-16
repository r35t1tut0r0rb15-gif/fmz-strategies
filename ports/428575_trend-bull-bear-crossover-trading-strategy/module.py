"""Daily vs monthly MA cross, broker days: SMA 7 of the close crossing above a 5-bar SMA of the last
completed month's close goes long; crossing below goes short.
Port of FMZ strategy #428575 "Trend Bull Bear Crossover Trading Strategy" (Mount MaV - Day MaV CrossOver).

FMZ source id: 428575

Source
    https://www.fmz.com/strategy/428575 (PineScript v4, FMZ last modified 2023-10-07 09:56:30).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 172-222), SMA, daily 7 bars, monthly 5 bars
    ln = security(ticker, "M", close) (lookahead off); lnma = sma(ln, 5) on the DAILY series; gnma = sma(close, 7)
    crossover(gnma, lnma) -> entry long; crossover(lnma, gnma) -> entry short (from 2020)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The monthly close is the last completed calendar month's (months of broker-day dates), used
      from the first day of the next month (lookahead off, months: the next period). The 5-bar SMA
      runs over daily bars of that step series, as written.
    * The year >= 2020 and date filters are backtest windows: dropped. strategy.entry reverses:
      REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; monthly values only after the month ends.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); months of broker-day dates.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428575_daily_vs_monthly_ma_cross"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "gbar": [7, 14],
    "abar": [5, 10],
}
DEFAULT_PARAMS = {"gbar": 7, "abar": 5}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    day = broker_day(bars_df.index)
    month = pd.PeriodIndex(day, freq="M")
    mclose = c.groupby(np.asarray(month)).last()
    prev_m = mclose.shift(1)                              # last completed month, from the next month on
    ln = pd.Series(prev_m.reindex(np.asarray(month)).to_numpy(), index=c.index)
    lnma = ln.rolling(int(p["abar"])).mean()
    gnma = c.rolling(int(p["gbar"])).mean()
    up = ((gnma > lnma) & (gnma.shift(1) <= lnma.shift(1))).to_numpy()
    dn = ((lnma > gnma) & (lnma.shift(1) <= gnma.shift(1))).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
