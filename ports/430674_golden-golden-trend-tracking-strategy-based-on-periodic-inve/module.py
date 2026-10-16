"""Buy-and-hold entry finder, broker days, long only: with MACD 12 / 26 at or below zero and the close's distance from its
EMA 200 not falling, a flat book goes long; strategy.close_all() runs on every bar, so each long is held for one bar.
Port of FMZ strategy #430674 "定投Golden趋势追踪策略Golden-Trend-Tracking-Strategy-Based-on-Periodic-Investment" (Buy and Hold entry finder Strategy).

FMZ source id: 430674

Source
    https://www.fmz.com/strategy/430674 (PineScript v4, FMZ last modified 2023-10-31 15:09:22).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 180-264), EMA 200, MACD 12 / 26, maximum EMA distance 50,000 (price units)
    longCondition = close - ema200 <= 50000 and (close - ema200) >= (close - ema200)[1] and macd <= 0
    longCondition and flat -> entry long;  (monthly adds while long)
    if true -> strategy.close_all()      (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * close_all on every bar acts on the position held at the start of the bar: a long entered on a
      signal bar fills at the next open and is closed at that bar's close (filled at the open after
      it); while it is open no new entry is taken (the monthly add branch needs a held position,
      which close_all removes on that bar). Ported as written: one-bar holds.
    * Criterion 2: the 50,000 price-unit cap on the distance is never binding on the header market
      (daily BTC never trades 50,000 above its EMA 200): not ported.
    * The strategy() line (pyramiding 10000) is commented out in the corpus copy: orders read as
      written (as #429505). The date range is unused (inDateRange = true). Long only; Opposite
      entries cannot occur. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close_all every bar as written.
    2 generic: ADAPT, the inert price-unit distance cap dropped.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out cash order size and pyramiding stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430674_dip_finder_one_bar_long"
FAMILY = "macd_momentum"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [200, 100],
    "macd_fast": [12, 8],
}
DEFAULT_PARAMS = {"ema_length": 200, "macd_fast": 12, "macd_slow": 26}


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
    dist = c - c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    cond = ((dist >= dist.shift(1)) & (macd <= 0)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if start == 0 and cond[i]:
            pos = 1
        if start != 0:                               # close_all on every bar
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
