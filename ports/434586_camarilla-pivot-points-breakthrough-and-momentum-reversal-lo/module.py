"""HPotter Camarilla side from the last completed broker day, 3-hour bars: a close above R1 = C + 1.1 R / 12 goes long, a
close below S1 = C - 1.1 R / 12 goes short; the side is held in between and reverses on the opposite break.
Port of FMZ strategy #434586 "Camarilla Pivot Points Breakthrough and Momentum Reversal Low Absorption Golden Cross Strategy" (Camarilla Pivot Points Backtest).

FMZ source id: 434586

Source
    https://www.fmz.com/strategy/434586 (PineScript v4, FMZ last modified 2023-12-07 16:57:11).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 129-170), resolution D; sell from R1, buy from S1; reverse false
    xHigh / xLow / xClose = security(res, high / low / close);  R1 = xClose + xRange 1.1 / 12;  S1 = xClose - xRange 1.1 / 12
    pos = close > R1 ? 1 : close < S1 ? -1 : pos[1];  1 -> entry long;  -1 -> entry short;  0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * security(..., 'D', x) without lookahead is read as the last completed broker day (17:00
      America/New_York), built from the port's own bars, as #429502. The side never returns to 0
      after the first break, so close_all only acts before it.
    * strategy.entry reverses: REVERSAL INTENDED. reverse is false. FREQ = "3h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days.
    2 generic: PASS, prior-day range levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily levels on broker days (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434586_camarilla_r1_s1_side"
FAMILY = "pivot_levels"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "level": [1, 2],
    "reverse": [False, True],
}
DEFAULT_PARAMS = {"level": 1, "reverse": False}


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


def _prev_day(bars_df):
    """High, low and close of the last completed broker day, on every bar of the next one."""
    day = broker_day(bars_df.index)
    g = pd.DataFrame({k: bars_df[k].to_numpy() for k in ("high", "low", "close")}, index=day)
    d = g.groupby(level=0).agg({"high": "max", "low": "min", "close": "last"}).shift(1)
    return tuple(d[k].reindex(day).to_numpy() for k in ("high", "low", "close"))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    dh, dl, dc = _prev_day(bars_df)
    div = {1: 12.0, 2: 6.0}[int(p["level"])]
    r1, s1 = dc + (dh - dl) * 1.1 / div, dc - (dh - dl) * 1.1 / div
    cv = bars_df["close"].to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        up, dn = cv > r1, cv < s1
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        tgt[i] = q
    if bool(p["reverse"]):
        tgt = -tgt
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
