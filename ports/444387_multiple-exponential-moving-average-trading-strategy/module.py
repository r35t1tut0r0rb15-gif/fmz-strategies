"""Four-EMA stack changes, daily bars, long only: from flat, the bar on which the EMA 55 becomes the lowest of EMA 8 / 13 / 21 / 55 goes long; the bar on which it becomes the highest closes.
Port of FMZ strategy #444387 "Multiple Exponential Moving Average Trading Strategy" (donmo's 4ema).

FMZ source id: 444387

Source
    https://www.fmz.com/strategy/444387 (PineScript v5, FMZ last modified 2024-03-11 16:17:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 137-177), EMA 8 / 13 / 21 / 55; margins 100 / 100
    emaLong = ema55 below the other three;  emaShort = ema55 above the other three;  change(emaLong) and emaLong and position_size <= 0 -> entry EL;  change(emaShort) and emaShort -> close EL

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.change of a condition is true on the bar it turns, so each signal is the first bar of the new
      stack. The entry is taken only when not long. The plotted levels never act. Long only. The margin
      settings are sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA stack changes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the margin settings stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_444387_four_ema_stack_turn_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_high": [55, 34],
    "ema_med": [21, 13],
}
DEFAULT_PARAMS = {"ema_lowest": 8, "ema_low": 13, "ema_med": 21, "ema_high": 55}


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
    e1, e2, e3, e4 = (c.ewm(span=int(p[k]), adjust=False).mean()
                      for k in ("ema_lowest", "ema_low", "ema_med", "ema_high"))
    up = ((e4 < e3) & (e4 < e2) & (e4 < e1)).to_numpy()
    dn = ((e4 > e3) & (e4 > e2) & (e4 > e1)).to_numpy()
    m = len(up)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(1, m):
        if up[i] and not up[i - 1] and not held:
            le[i] = True
        elif dn[i] and not dn[i - 1] and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
