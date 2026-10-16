"""Higher-high breakout, long only, broker days: from flat, a high above the previous high after a lower-or-equal
high, with a rising SMA 20, MACD and MACD signal, goes long; a falling stochastic %K closes the long.
Port of FMZ strategy #429459 "Trend Following Buy and Sell Strategy" (Higher High / Lower Low Strategy).

FMZ source id: 429459

Source
    https://www.fmz.com/strategy/429459 (PineScript v4, FMZ last modified 2023-10-17 12:59:59).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 141-174), SMA 20, %K 5 (smoothed 2), MACD 5 / 20 / 30, long only
    flat and high[2] >= high[1] and high > high[1] and sma20 rising and macd rising and signal rising -> order long
    in a position and k < k[1] -> order short (closes the long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.order by net effect: the sell order of the same size only closes the long. Only from
      flat (position_size == 0) for the entry; the exit only while in a position.
    * `month >= 10 and year >= 2020` is the author's backtest-start filter (October 2020): dropped.
      The short branch is off (longOnly true).
    * Long only. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, high comparisons and indicator slopes only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429459_higher_high_long"
FAMILY = "momentum_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period_a": [20, 50],
    "period_k": [5, 14],
}
DEFAULT_PARAMS = {"period_a": 20, "period_k": 5, "smooth_k": 2, "smooth_d": 3, "fast": 5, "slow": 20, "signal": 30}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e = lambda x, n: x.ewm(span=int(n), adjust=False).mean()  # noqa: E731
    ma = c.rolling(int(p["period_a"])).mean()
    n = int(p["period_k"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["smooth_k"])).mean() - 50
    d = k.rolling(int(p["smooth_d"])).mean()
    macd = e(c, p["fast"]) - e(c, p["slow"])
    sig = e(macd, p["signal"])
    ok = (k.notna() & d.notna() & macd.notna() & sig.notna()).to_numpy()
    entry = ((h.shift(2) >= h.shift(1)) & (h > h.shift(1)) & (ma > ma.shift(1)) & (macd > macd.shift(1))
             & (sig > sig.shift(1))).to_numpy()
    leave = (k < k.shift(1)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if not ok[i]:
            continue
        was = held
        if not was and entry[i]:
            le[i], held = True, True
        if was and leave[i]:
            lx[i], held = True, False
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
