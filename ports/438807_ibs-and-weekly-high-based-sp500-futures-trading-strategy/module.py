"""Monday weak-close buys, 1-hour bars, long only: from flat, on a Monday (UTC) bar with the close under the weekly close from the security call and an internal bar strength under 0.5, buy; close when a
close is above the previous high or four bars after the signal.
Port of FMZ strategy #438807 "IBS and Weekly High Based SP500 Futures Trading Strategy" (Hobbiecode - SP500 IBS + Higher).

FMZ source id: 438807

Source
    https://www.fmz.com/strategy/438807 (PineScript v5, FMZ last modified 2024-01-15 14:42:00).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 147-167), IBS < 0.5; weekly close[1]; exit after 4 bars or a close above the previous high
    isMonday;  ibs = (close - low) / (high - low);  prevFridayClose = security(tickerid, "W", close[1]);  monday and close < it and ibs < 0.5 and position_size < 1 -> entry Buy
    (close > high[1] or barssince(entry condition) == 4) and long -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-5 security() without lookahead is read as the last completed higher bar; its expression
      close[1] is then the week before that, so the value is the close of the broker week two weeks back
      (a broker week runs Monday to Friday by broker-day label, as #437025), built from the module's own
      bars. dayofweek is read on the bar's UTC open time (as #435514). The 4-bar exit counts chart bars
      (hours), as written. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly value from completed weeks.
    2 generic: PASS, weekday, IBS and close tests.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: UTC weekday of the bar (Monday entries); broker weeks for the weekly close.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438807_monday_ibs_weekly_close_long"
FAMILY = "calendar_seasonal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ibs_max": [0.5, 0.3],
    "hold_bars": [4, 8],
}
DEFAULT_PARAMS = {"ibs_max": 0.5, "hold_bars": 4}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")   # the Monday of the broker week
    wk_close = c.groupby(week).last()
    wc = wk_close.shift(2).reindex(week).to_numpy()        # completed week, then [1]
    with np.errstate(divide="ignore", invalid="ignore"):
        ibs = ((c - lo) / (h - lo)).to_numpy()
    monday = bars_df.index.tz_convert("UTC").dayofweek == 0
    cv, hv = c.to_numpy(dtype=float), h.to_numpy(dtype=float)
    hold, imax = int(p["hold_bars"]), float(p["ibs_max"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend_e, pend_x, last_sig = 0, False, False, -10 ** 9
    for i in range(m):
        if pend_x:                                       # orders of the last bar fill at this open
            pos, pend_x = 0, False
        if pend_e:
            pos, pend_e = 1, False
        enter = monday[i] and cv[i] < wc[i] and ibs[i] < imax and pos == 0
        if enter:
            last_sig = i
        if enter and i + 1 < m:
            le[i], pend_e = True, True
        elif pos == 1 and ((i > 0 and cv[i] > hv[i - 1]) or i - last_sig == hold):
            lx[i], pend_x = True, True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
