"""EMA 9 / 21 crossings, broker days: the up-cross goes long and the down-cross goes short; a close 1 % back from the best close since the signal closes the held side; reversing.
Port of FMZ strategy #491505 "EMA Crossover Dynamic Trailing Stop Loss Strategy" (EMA Crossover Strategy with Trailing Stop and Alerts).

FMZ source id: 491505

Source
    https://www.fmz.com/strategy/491505 (PineScript v6, FMZ last modified 2025-04-21 15:53:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 178-238), EMA 9 / 21; close trail 1 %
    crossover -> highest := close, entry Buy;  crossunder -> lowest := close, entry Sell
    long: highest := max(highest, close), close < highest x 0.99 -> close Buy;  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail is a ratchet of closes from the signal close, tested on closes and sent as a close (an exit
      signal, no stop module); a loop follows the position and the kept extremes, as written. An entry on
      the other side reverses (REVERSAL INTENDED). No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested trail.
    2 generic: PASS, EMA crossings with a close-based trail.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
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

NAME = "fmz_491505_ema9_21_cross_close_trail1pct_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trailStopPercent": [1.0, 3.0],
    "emaLength2": [21, 50],
}
DEFAULT_PARAMS = {"trailStopPercent": 1.0, "emaLength2": 21, "emaLength1": 9}


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
    c = bars_df["close"]
    f = c.ewm(span=int(p["emaLength1"]), adjust=False).mean()
    s = c.ewm(span=int(p["emaLength2"]), adjust=False).mean()
    buy = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    sell = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    q = float(p["trailStopPercent"]) / 100
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, nxt = 0, 0
    hp = lp = np.nan
    for i in range(m):
        pos = nxt
        if buy[i]:
            hp = cv[i]
        if sell[i]:
            lp = cv[i]
        if pos > 0:
            hp = max(hp, cv[i])
            if cv[i] < hp * (1 - q):
                lx[i], nxt = True, 0
        if pos < 0:
            lp = min(lp, cv[i])
            if cv[i] > lp * (1 + q):
                sx[i], nxt = True, 0
        if buy[i]:
            le[i], nxt = True, 1
        if sell[i]:
            se[i], nxt = True, -1
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le), S(lx & ~se & ~le), S(se), S(sx & ~le & ~se)


def portfolio_kwargs(**params):
    return {}
