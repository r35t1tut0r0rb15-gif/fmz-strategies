"""Turtle-style Donchian breakout, long only, broker days: a close at or above the previous 20-bar high goes long; a
close at or below the previous 10-bar low, or 1 ATR below the previous close, closes it.
Port of FMZ strategy #429512 "Breakout Strategy Based on Turtle Trading" (Turtle trading strategy (Donchian/ATR)).

FMZ source id: 429512

Source
    https://www.fmz.com/strategy/429512 (PineScript v3, FMZ last modified 2023-10-17 17:22:34).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 214-254), enter channel 20, exit channel 10, ATR 20 x 2 (the stop line uses 1 ATR), direction Long
    break_up = close >= highest(20)[1] -> entry long
    break_down = close <= lowest(10)[1] or stop = close <= (close - atr(20))[1] -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop line is close - 1 x ATR (the multiplier input is not used in it, as written); it is
      checked on closes, so it is an exit signal (rule 3), not a stop order.
    * Direction defaults to Long. Long only. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, channel levels and an ATR distance.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 1-unit quantity stored.
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

NAME = "fmz_429512_turtle_donchian_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "enter_period": [20, 55],
    "exit_period": [10, 20],
}
DEFAULT_PARAMS = {"enter_period": 20, "exit_period": 10, "atr_period": 20}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, int(p["atr_period"]))
    up = (c >= h.rolling(int(p["enter_period"])).max().shift(1)).to_numpy()
    dn = (c <= lo.rolling(int(p["exit_period"])).min().shift(1)).to_numpy()
    stop = (c <= (c - atr).shift(1)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if held and (dn[i] or stop[i]):
            lx[i], held = True, False
        elif not held and up[i]:
            le[i], held = True, True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
