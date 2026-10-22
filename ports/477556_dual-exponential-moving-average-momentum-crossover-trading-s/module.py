"""Crossings of two triple-smoothed EMAs (300 / 500, as written), broker days, entries only from flat: the cross up goes long and the cross down closes it; a cross down from flat goes short and a cross up closes it.
Port of FMZ strategy #477556 "Dual Exponential Moving Average Momentum Crossover Trading Strategy" (TEMA Strategy for Gold).

FMZ source id: 477556

Source
    https://www.fmz.com/strategy/477556 (PineScript v6, FMZ last modified 2025-01-06 13:53:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-146), "TEMA" 300 / 500 = ema(2 ema - ema(ema), n); swing stop levels and pip value computed but unused
    crossover(t300, t500) and flat -> entry Long;  crossunder and flat -> entry Short;  long and crossunder -> close Long;  short and crossover -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "TEMA" is the EMA of (2 EMA - EMA of EMA), as written (a smoothed DEMA). The swing-low / high
      stop levels are computed and never sent. Entries need a flat position at the bar's close, so the
      opposite crossing only closes: after the first trade the strategy alternates between one side and
      flat. Opposite entries cannot occur (entries only from flat). No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the pip value input is unused.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477556_smoothed_dema300_500_cross_flat_only"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [300, 50],
    "long_len": [500, 200],
}
DEFAULT_PARAMS = {"short_len": 300, "long_len": 500}


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


def _tema(c, n):
    e = c.ewm(span=n, adjust=False).mean()
    ee = e.ewm(span=n, adjust=False).mean()
    return (2 * e - ee).ewm(span=n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a, b = _tema(c, int(p["short_len"])), _tema(c, int(p["long_len"]))
    up = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    dn = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    m = len(up)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if up[i] and pos == 0:
            le[i], nxt = True, 1
        if dn[i] and pos == 0:
            se[i], nxt = True, -1
        if pos == 1 and dn[i]:
            lx[i], nxt = True, 0
        if pos == -1 and up[i]:
            sx[i], nxt = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
