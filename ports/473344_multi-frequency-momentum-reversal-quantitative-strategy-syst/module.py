"""Losing-streak buys held a fixed time, 2-day bars, long only: after 8 non-doji closes in a row under the previous close (counted while flat), a buy is held 7 bars and then closed.
Port of FMZ strategy #473344 "Multi Frequency Momentum Reversal Quantitative Strategy System Multi Frequency Momentum Reversal Quantitative Strategy System" (Streak-Based Trading Strategy).

FMZ source id: 473344

Source
    https://www.fmz.com/strategy/473344 (PineScript v5, FMZ last modified 2024-11-29 14:47:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-156), direction Long; streak 8; hold 7 bars; doji body < 0.01 % of the range
    flat: count win / loss streaks (reset on a doji or unchanged close);  in position: hold -= 1, hold <= 0 -> close_all, streaks := 0;  flat and loss_streak >= 8 -> entry Long, hold := 7

Interpretation choices (Pine rules in SURVEY_README.md)
    * The streaks, the position flag and the hold counter are followed in a loop, in the written order:
      the close comes before the entry test, so no entry on the closing bar. A doji test on a bar with
      no range is na and false, as Pine. The "Short" direction option (win streaks) is a separate
      setting, not ported (default Long). Long only. No sizing code. FREQ = "2D" from the backtest header
      (blocks of 2 broker days, as #429148).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, losing-streak entries with a time exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_473344_loss_streak8_hold7_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "streak": [8, 5],
    "hold": [7, 3],
}
DEFAULT_PARAMS = {"streak": 8, "hold": 7, "doji_pct": 0.01, "days": 2}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    doji = ((c - o).abs() / (h - lo) < float(p["doji_pct"]) / 100).to_numpy()
    win = ((c > c.shift(1)).to_numpy()) & ~doji
    loss = ((c < c.shift(1)).to_numpy()) & ~doji
    th, hold = int(p["streak"]), int(p["hold"])
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    ws = ls = cnt = 0
    inpos = False
    for i in range(m):
        if not inpos:
            if win[i]:
                ws, ls = ws + 1, 0
            elif loss[i]:
                ls, ws = ls + 1, 0
            else:
                ws = ls = 0
        if inpos:
            cnt -= 1
            if cnt <= 0:
                lx[i], inpos, ws, ls = True, False, 0, 0
        if not inpos and ls >= th:
            le[i], inpos, cnt = True, True, hold
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
