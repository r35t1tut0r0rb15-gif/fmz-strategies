"""EMA 10 / 20 / 30 "perfect order" starts and ends, broker days: when the three EMAs first stack upward the strategy
goes long, when they first stack downward it goes short, and when the stack it entered on breaks everything closes.
Port of FMZ strategy #489007 "多重指数移动平均线趋势反转交易策略-Multi-EMA-Trend-Reversal-Trading-Strategy" (Perfect Order Strategy).

FMZ source id: 489007

Source
    https://www.fmz.com/strategy/489007 (PineScript v6, FMZ last modified 2025-04-01 10:02:12).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 136-192), EMA 10 / 20 / 30
    up = emaA > emaB > emaC;  down = emaA < emaB < emaC
    if up and not wasUp -> entry long (wasUp, not wasDown);  else if down and not wasDown -> entry short
    else if (not up and wasUp) or (not down and wasDown) -> close_all (once), clear the flags;  else if neither -> clear

Interpretation choices (Pine rules in SURVEY_README.md)
    * The if / else-if chain as written: a new opposite stack on the bar the old one breaks is an entry (reversal),
      not an end. The close_all runs only in its own branch.
    * REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first minute;
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs only.
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

NAME = "fmz_489007_ema_perfect_order_start_end"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "a": [10, 5],
    "c": [30, 50],
}
DEFAULT_PARAMS = {"a": 10, "b": 20, "c": 30}


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
    ea, eb, ec = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("a", "b", "c"))
    up = ((ea > eb) & (eb > ec)).to_numpy()
    dn = ((ea < eb) & (eb < ec)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos, was_up, was_dn, end_done = 0, False, False, False
    for i in range(m):
        if up[i] and not was_up:
            pos, was_up, was_dn, end_done = 1, True, False, False
        elif dn[i] and not was_dn:
            pos, was_dn, was_up, end_done = -1, True, False, False
        elif (not up[i] and was_up) or (not dn[i] and was_dn):
            if not end_done:
                pos, end_done = 0, True
            was_up = was_dn = False
        elif not up[i] and not dn[i]:
            was_up = was_dn = end_done = False
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
