"""Close crosses of any of four SMAs, broker days: the close crossing above the SMA 21, 50, 100 or 200 goes long, crossing
below any of them goes short; always in once started (the source's exit orders can never be placed).
Port of FMZ strategy #432874 "Multi Moving Average Breakout Strategy" (DolarBasar by AlperDursun).

FMZ source id: 432874

Source
    https://www.fmz.com/strategy/432874 (PineScript v5, FMZ last modified 2023-11-22 13:41:38).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 119-156), SMA 21 / 50 / 100 / 200; stop 0.995 x lowest(low, 2), target from a 2-bar range
    crossover(close, any SMA) -> entry long;  crossunder(close, any SMA) -> entry short
    low < 0.995 x lowest(low, 2) or high > lowest(low, 2) + 3 x (highest(high, 2) - lowest(low, 2)) -> exit(stop, limit)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit orders are placed only when their condition holds, and it never can: lowest(low, 2)
      includes the current low (so low < 0.995 x it is false) and the target is at least the 2-bar
      high (so high > it is false). Positions change only by the opposite entry.
    * On a bar crossing one SMA up and another down, the short (written later) wins.
      strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the unreachable exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: DG432874 (2 members, best partner #441008, Jaccard 0.925); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432874_four_sma_close_cross"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "set": [0, 1],
}
DEFAULT_PARAMS = {"set": 0}
SETS = {0: (21, 50, 100, 200), 1: (10, 20, 50, 100)}


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
    up = pd.Series(False, index=c.index)
    dn = pd.Series(False, index=c.index)
    for n in SETS[int(p["set"])]:
        s = c.rolling(n).mean()
        up |= (c > s) & (c.shift(1) <= s.shift(1))
        dn |= (c < s) & (c.shift(1) >= s.shift(1))
    x, y = up.to_numpy(), dn.to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if x[i]:
            pos = 1
        if y[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
