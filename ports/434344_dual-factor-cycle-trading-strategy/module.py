"""HPotter combo of the 123 reversal and Hartle's support / resistance cue, 1-hour bars: long while both sides say up, short
while both say down, flat otherwise. The cue side turns down when a bar's high is at or under the last completed broker
week's low and up when its low is at or above that week's high.
Port of FMZ strategy #434344 "Dual factor Cycle Trading Strategy" (Combo Backtest 123 Reversal & Cueing Off Support And Resistance Levels).

FMZ source id: 434344

Source
    https://www.fmz.com/strategy/434344 (PineScript v4, FMZ last modified 2023-12-05 17:56:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 170-210), stoch 14 / 1 / 3, level 50; weekly high[1] / low[1]; "To Line" true; reverse false
    p123 as Reversal123(14, 1, 3, 50);  cosrl = high <= weekLow[1] ? -1 : low >= weekHigh[1] ? 1 : cosrl[1]
    both 1 -> entry long;  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * security(..., "W", high[1] / low[1]) reads the last completed week: the last completed broker
      week (broker days from Monday on, 17:00 America/New_York), built from the port's own bars, so
      each value is known from the next week's first bar (approximation stated).
    * Each side keeps its last state until it changes. strategy.entry reverses: REVERSAL INTENDED.
      The "To Line" choice is the default. reverse is false. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly values from completed broker weeks.
    2 generic: PASS, oscillator levels and prior-week levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: weekly levels on broker weeks (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434344_combo_123_cosrl_weekly"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "to_line": [True, False],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "to_line": True}


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


def _hold(cond_up, cond_dn):
    m = len(cond_up)
    out = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if cond_up[i]:
            q = 1
        elif cond_dn[i]:
            q = -1
        out[i] = q
    return out


def _prev_week_hl(bars_df):
    """High and low of the last completed broker week, on every bar of the next one."""
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")
    g = pd.DataFrame({"high": bars_df["high"].to_numpy(), "low": bars_df["low"].to_numpy()}, index=week)
    agg = g.groupby(level=0).agg({"high": "max", "low": "min"}).shift(1)
    return (pd.Series(agg["high"].reindex(week).to_numpy(), index=bars_df.index),
            pd.Series(agg["low"].reindex(week).to_numpy(), index=bars_df.index))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    p123 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())
    wh, wl = _prev_week_hl(bars_df)
    if bool(p["to_line"]):
        dn, up = (h <= wl).to_numpy(), (lo >= wh).to_numpy()
    else:
        dn, up = (h <= wh).to_numpy(), (lo >= wl).to_numpy()
    cos = _hold(up & ~dn, dn)
    tgt = np.where((p123 == 1) & (cos == 1), 1, np.where((p123 == -1) & (cos == -1), -1, 0)).astype(np.int8)
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
