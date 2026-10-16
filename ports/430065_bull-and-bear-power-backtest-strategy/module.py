"""Elder ray bull power, 1-hour bars: the day's running high minus an EMA 13 of the close above zero holds a long, below
zero holds a short.
Port of FMZ strategy #430065 "Bull and Bear Power Backtest Strategy" (Elder Ray (Bull Power) Strategy Backtest).

FMZ source id: 430065

Source
    https://www.fmz.com/strategy/430065 (PineScript v2, FMZ last modified 2023-10-24 16:43:52).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 138-173), EMA 13, trigger 0
    DayHigh = dayofmonth != dayofmonth[1] ? high : max(high, DayHigh[1])
    nRes = DayHigh - ema(close, 13)
    nRes > 0 -> entry long;  nRes < 0 -> entry short;  else pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * The day is the broker day (the session ending 17:00 America/New_York, DST by the zone): the
      running high restarts on the first bar of each broker day (the source's calendar day of the
      chart's exchange time zone; a declared clock time per skill section 5).
    * "Trade reverse" defaults to false and is fixed. strategy.entry reverses: REVERSAL INTENDED.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a price minus its moving average, compared with zero.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: ND430065 (2 members, best partner #438463, Jaccard 0.721); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) restarts the day high; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430065_elder_bull_power_day_high"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [13, 8, 26],
}
DEFAULT_PARAMS = {"length": 13, "trigger": 0.0}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, c = bars_df["high"], bars_df["close"]
    day_high = h.groupby(broker_day(bars_df.index)).cummax()
    res = (day_high - c.ewm(span=int(p["length"]), adjust=False).mean()).to_numpy()
    trig = float(p["trigger"])
    m = len(res)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if res[i] > trig:
            pos = 1
        elif res[i] < trig:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
