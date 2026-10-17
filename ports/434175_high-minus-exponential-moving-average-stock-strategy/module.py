"""HPotter high-minus-EMA state, broker days: when the previous day's high was above the previous day's EMA 13 of the closes
the state is long, below it short; always in.
Port of FMZ strategy #434175 "High Minus Exponential Moving Average Stock Strategy" (High - EMA Strategy Backtest).

FMZ source id: 434175

Source
    https://www.fmz.com/strategy/434175 (PineScript v2, FMZ last modified 2023-12-04 14:29:31).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 141-154), length 13, reverse false
    nRes = high[1] - nz(ema(close, 13)[1]);  pos = nRes > 0 ? 1 : nRes < 0 ? -1 : pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both terms are read one bar back, as written (one extra bar of delay before the engine's lag).
      strategy.entry reverses: REVERSAL INTENDED. reverse is false. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, the high against an average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: ND433079 (2 members, best partner #433079, Jaccard 0.670); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434175_high_minus_ema_state"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [13, 26, 50],
}
DEFAULT_PARAMS = {"length": 13}


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
    h, c = bars_df["high"], bars_df["close"]
    e = c.ewm(span=int(p["length"]), adjust=False).mean()
    res = (h.shift(1) - e.shift(1).fillna(0.0)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if res[i] > 0:
            pos = 1
        elif res[i] < 0:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
