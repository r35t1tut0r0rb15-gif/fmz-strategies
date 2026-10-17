"""Daily pivot breaks, 1-hour bars: from the last completed broker day's high, low and close the pivot levels are built;
a close above R1 turns the state long, a close below S1 short; always in after the first break.
Port of FMZ strategy #433589 "Dynamic Support and Resistance Strategy Based on Historical Data" (Pivot Point V2).

FMZ source id: 433589

Source
    https://www.fmz.com/strategy/433589 (PineScript v4, FMZ last modified 2023-11-28 17:04:16).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 142-173), resolution D, sell from R1, buy from S1, reverse false
    xHigh / xLow / xClose = security(tickerid, 'D', high / low / close);  PP = (H + L + C) / 3;  S1 = 2 PP - H;  R1 = 2 PP - L
    pos = close > R1 ? 1 : close < S1 ? -1 : pos[1];  1 -> long;  -1 -> short;  0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * security(..., 'D') without lookahead is read as the last completed daily bar (SURVEY_README),
      built from the port's own bars on broker days (17:00 America/New_York). The state is 0 only
      before the first break.
    * As written the long side buys above the "sell from" level (R1) and the short sells below the
      "buy from" level (S1): a breakout reading. strategy.entry reverses: REVERSAL INTENDED. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days.
    2 generic: PASS, the close against daily pivot levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily values on broker days (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433589_daily_pivot_break"
FAMILY = "pivot_levels"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "level": ["1", "2"],
}
DEFAULT_PARAMS = {"level": "1"}


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
    day = broker_day(bars_df.index)
    g = pd.DataFrame({k: bars_df[k].to_numpy() for k in ("high", "low", "close")}, index=day)
    d = g.groupby(level=0).agg({"high": "max", "low": "min", "close": "last"}).shift(1)
    pp = (d["high"] + d["low"] + d["close"]) / 3
    s1, r1 = 2 * pp - d["high"], 2 * pp - d["low"]
    if str(p["level"]) == "2":
        s, b = pp - (r1 - s1), pp + (r1 - s1)
    else:
        s, b = s1, r1
    sv = s.reindex(day).to_numpy()
    bv = b.reindex(day).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if cv[i] > bv[i]:
            pos = 1
        elif cv[i] < sv[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
