"""Noro's weekly and daily levels, 1-hour bars: with the whole bar above both the last completed broker week's ohlc4 and
the last completed broker day's ohlc4, a red bar goes long; with the whole bar below both, a green bar goes short.
Port of FMZ strategy #432232 "Cross Timeframe Double Breakout Levels Strategy" (Noro's Levels Strategy v1.0).

FMZ source id: 432232

Source
    https://www.fmz.com/strategy/432232 (PineScript v2, FMZ last modified 2023-11-15 17:27:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 238-273), timeframes W and D, source ohlc4, antipila on, colour filter on
    level = security(tickerid, 'W', ohlc4[1]);  level2 = security(tickerid, 'D', ohlc4[1])
    low > level and low > level2 and close < open -> entry long
    high < level and high < level2 and close > open -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * security(..., src[1]) reads the previous higher bar: the last completed broker week and broker
      day (17:00 America/New_York), built from the port's own bars (the higher bar's first open,
      highest high, lowest low and last close), so each value is known from the next higher bar's
      first bar on. A week is the broker days from Monday on.
    * "antipila" on uses the whole bar (low above / high below); the colour filter on needs a counter
      bar. strategy.entry reverses: REVERSAL INTENDED. The lot formula is sizing; the date inputs
      (1900 to 2100) are the author's window: dropped. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; higher-timeframe values from completed broker weeks / days.
    2 generic: PASS, the bar against prior-period levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, the capital % input and the lot formula stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: weekly and daily levels on broker weeks / days (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432232_noro_week_day_levels"
FAMILY = "pivot_levels"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "antipila": [True, False],
    "color_filter": [True, False],
}
DEFAULT_PARAMS = {"antipila": True, "color_filter": True}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _prev_ohlc4(bars_df, label):
    """ohlc4 of the last completed higher bar (grouped by label), on every bar of the next one."""
    g = pd.DataFrame({k: bars_df[k].to_numpy() for k in ("open", "high", "low", "close")}, index=label)
    agg = g.groupby(level=0).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    o4 = ((agg["open"] + agg["high"] + agg["low"] + agg["close"]) / 4).shift(1)
    return pd.Series(o4.reindex(label).to_numpy(), index=bars_df.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")
    lw, ld = _prev_ohlc4(bars_df, week), _prev_ohlc4(bars_df, day)
    if bool(p["antipila"]):
        up1, dn1, up2, dn2 = lo > lw, h < lw, lo > ld, h < ld
    else:
        up1, dn1, up2, dn2 = c > lw, c < lw, c > ld, c < ld
    cf = bool(p["color_filter"])
    x = (up1 & up2 & ((c < o) | (not cf))).to_numpy()
    y = (dn1 & dn2 & ((c > o) | (not cf))).to_numpy()
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
