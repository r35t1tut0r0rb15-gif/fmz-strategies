"""Camarilla H4 / L4 breakout, hourly bars: a close above the previous broker day's H4 (close + 1.1 x range
/ 2) goes long, a close below its L4 goes short.
Port of FMZ strategy #428790 "A Momentum Breakout Strategy" (ASH1Strategy).

FMZ source id: 428790

Source
    https://www.fmz.com/strategy/428790 (PineScript v4, FMZ last modified 2023-10-09 15:15:22).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 201-267), daily H4 / L4 = close +/- (high - low) x 1.1 / 2
    dtime_h4 = security(tickerid, 'D', h4[1]); dtime_l4 = security(tickerid, 'D', l4[1])
    close > dtime_h4 -> entry long; close < dtime_l4 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * security('D', x[1]) without lookahead is the last completed day: built inside simulate() from
      the port's own bars grouped by broker day (17:00 America/New_York), shifted one day.
    * The other pivots (H1-H6, L1-L6, the pivot) and the EMA 3 are drawn only.
    * strategy.entry reverses: REVERSAL INTENDED; same-direction entries while in a position are
      ignored. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily levels from completed broker days.
    2 generic: PASS, levels from the day's own range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: DG428790 (3 members, best partner #437664, Jaccard 0.970); ND428790 (2 members, best partner #434487, Jaccard 0.789); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily levels on broker days (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428790_camarilla_h4_l4_breakout"
FAMILY = "pivot_levels"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "frac": [0.5, 0.25],
}
DEFAULT_PARAMS = {"frac": 0.5, "width": 1.1}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    lab = broker_day(bars_df.index)
    day = bars_df.groupby(lab).agg({"high": "max", "low": "min", "close": "last"})
    k = float(p["width"]) * float(p["frac"])
    h4 = (day["close"] + (day["high"] - day["low"]) * k).shift(1)   # the last completed broker day
    l4 = (day["close"] - (day["high"] - day["low"]) * k).shift(1)
    dh4 = pd.Series(h4.reindex(lab).to_numpy(), index=bars_df.index)
    dl4 = pd.Series(l4.reindex(lab).to_numpy(), index=bars_df.index)
    long_e = (c > dh4).astype(bool)
    short_e = (c < dl4).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
