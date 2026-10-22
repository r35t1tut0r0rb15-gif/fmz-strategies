"""Closes beyond a one-bar swing line and any Fibonacci retracement of the 50-bar range, daily bars, long only: a close above the swing line and above any of the 23.6-78.6 % levels goes long; a close
below the line and below any of them closes.
Port of FMZ strategy #449846 "Fibonacci Golden Ratio Retracement Buying Strategy" (Fibonacci BFSP).

FMZ source id: 449846

Source
    https://www.fmz.com/strategy/449846 (PineScript v5, FMZ last modified 2024-04-29 17:08:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-164), Fibonacci levels of the 50-bar high / low; swing 1
    avd = close > high[1] ? 1 : close < low[1] ? -1 : 0;  avn = last nonzero avd;  tsl = avn == 1 ? low : high
    buy = close > tsl and close above any fib level -> entry Buy;  sell = close < tsl and close below any fib level -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * With swing length 1 the line is the bar's own low after an up-break and its own high after a
      down-break, as written, so the buy needs the close above the bar's low (after an up-break) and
      above the lowest of the five levels. A same-bar close only acts on a held long. Long only. No
      sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, swing-line and Fibonacci-level closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449846_swing_line_fib_level_close_long"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "price_len": [50, 100],
    "swing": [1, 5],
}
DEFAULT_PARAMS = {"price_len": 50, "swing": 1}
FIBS = (0.236, 0.382, 0.5, 0.618, 0.786)


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
    n = int(p["price_len"])
    ph, pl = h.rolling(n).max(), lo.rolling(n).min()
    rng = ph - pl
    above = pd.Series(False, index=c.index)
    below = pd.Series(False, index=c.index)
    for f in FIBS:
        lvl = ph - f * rng
        above |= c > lvl
        below |= c < lvl
    k = int(p["swing"])
    res, sup = h.rolling(k).max(), lo.rolling(k).min()
    avd = np.where(c > res.shift(1), 1.0, np.where(c < sup.shift(1), -1.0, 0.0))
    avn = np.full(len(avd), np.nan)
    last = np.nan
    for i in range(len(avd)):
        if avd[i] != 0:
            last = avd[i]
        avn[i] = last
    tsl = pd.Series(np.where(avn == 1, sup.to_numpy(), res.to_numpy()), index=c.index)
    go = ((c > tsl) & above).to_numpy()
    out = ((c < tsl) & below).to_numpy()
    m = len(go)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if go[i] and not held:
            le[i] = True                     # a same-bar close acts only on a held long
        elif out[i] and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
