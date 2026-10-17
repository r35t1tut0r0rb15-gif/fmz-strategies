"""Inverted daily close comparison, 4-hour bars: a close above the reference daily close goes short, a close below it goes
long; always in after the first signal. The reference is security(..., "D", close[1]), read as the close of the broker
day before the last completed one.
Port of FMZ strategy #433117 "Inverse Las Vegas Algorithmic Trading Strategy" (Las Vegas LS-Invertida-Reinversion).

FMZ source id: 433117

Source
    https://www.fmz.com/strategy/433117 (PineScript v4, FMZ last modified 2023-11-24 15:19:03).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 185-220), length 14 and offset 1 unused; reference security('D', close[1])
    previous_price = security(tickerid, 'D', close[1]);  close > previous_price -> entry short;  close < previous_price -> entry long
    (the capital / gains bookkeeping only feeds variables, not orders)

Interpretation choices (Pine rules in SURVEY_README.md)
    * security(..., 'D', close[1]) without lookahead is read as the value of the last completed daily
      bar (SURVEY_README: higher timeframes from completed higher bars), i.e. close[1] as of that day:
      the close two broker days back (17:00 America/New_York), built from the port's own bars.
    * The "reinvestment" variables are bookkeeping; the orders use the default quantity. strategy.entry
      reverses: REVERSAL INTENDED. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days.
    2 generic: PASS, a close against an earlier close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital bookkeeping stored in original_sizing.txt.
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

NAME = "fmz_433117_inverted_daily_close_compare"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lag_days": [1, 0],
}
DEFAULT_PARAMS = {"lag_days": 1}


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
    dc = pd.Series(c.to_numpy(), index=day).groupby(level=0).last()
    ref = pd.Series(dc.shift(1 + int(p["lag_days"])).reindex(day).to_numpy(), index=c.index)
    up, dn = (c > ref).to_numpy(), (c < ref).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = -1
        elif dn[i]:
            pos = 1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
