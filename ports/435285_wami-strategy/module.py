"""WAMI momentum sign, broker days: a doubly EMA-smoothed WMA of the one-bar momentum above the trigger holds a long, below it a
short (reversing); at the trigger the last side is kept; the "Trade reverse" input flips the side.
Port of FMZ strategy #435285 "WAMI Strategy" (WAMI Strategy).

FMZ source id: 435285

Source
    https://www.fmz.com/strategy/435285 (PineScript v2, FMZ last modified 2023-12-13 17:42:01).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 147-162), WMA 4 of the 1-bar change, EMA 13 twice; trigger 0
    xWAMI = ema(ema(wma(mom(close, 1), 4), 13), 13);  pos = xWAMI > Trigger ? 1 : xWAMI < Trigger ? -1 : nz(pos[1], 0);  possig = reverse ? -pos : pos
    possig == 1 -> entry long;  possig == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state holds until the opposite sign; strategy.entry reverses: REVERSAL INTENDED. The signal
      is sent on the change of state only. The trigger 0 is a threshold on a price change (the sign
      of the smoothed momentum). Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, momentum sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435285_wami_sign"
FAMILY = "momentum_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "length_ema": [13, 8],
}
DEFAULT_PARAMS = {"reverse": False, "length_ema": 13, "length_wma": 4, "trigger": 0.0}


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


def _wma(s, n):
    w = np.arange(1, n + 1, dtype=float)
    return s.rolling(n).apply(lambda a: float(np.dot(a, w) / w.sum()), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e = int(p["length_ema"])
    x = _wma(c.diff(), int(p["length_wma"])).ewm(span=e, adjust=False).mean().ewm(span=e, adjust=False).mean().to_numpy()
    trg = float(p["trigger"])
    m = len(x)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if x[i] > trg:
            q = 1
        elif x[i] < trg:
            q = -1
        tgt[i] = q
    if p["reverse"]:
        tgt = -tgt
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
