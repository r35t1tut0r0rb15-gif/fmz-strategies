"""Volatility-stop trend flips, broker days: a ratcheting stop line sits 2 ATR 20 below the highest close of the up trend
(above the lowest close of the down trend); the close crossing it flips the trend; the strategy is long in the up trend
and short in the down trend.
Port of FMZ strategy #433959 "Volatility Stop Tracking Strategy" (Volatility stop strategy).

FMZ source id: 433959

Source
    https://www.fmz.com/strategy/433959 (PineScript v4, FMZ last modified 2023-12-01 17:53:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 126-180), length 20, mult 2; take profit and stop loss off
    max1 = max(nz(max_[1]), close);  min1 = min(nz(min_[1]), close);  up_prev = nz(is_uptrend[1], true)
    stop = up_prev ? max1 - 2 atr : min1 + 2 atr;  vstop1 = up_prev ? max(nz(vstop[1]), stop) : min(nz(vstop[1]), stop);  is_uptrend = close - vstop1 >= 0
    on a change: max_ = min_ = close, vstop = up ? close - 2 atr : close + 2 atr;  else vstop = vstop1
    is_uptrend -> entry long;  not is_uptrend -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Transcribed as written, including the nz(..) seeds of 0 (min_ starts at 0 until the first trend
      change) and Pine's handling of undefined values (an undefined comparison is false).
    * The entries are levels (re-fired every bar, ignored while in that position). strategy.entry
      reverses: REVERSAL INTENDED. The percent / pip exits are off. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR trailing line.
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

NAME = "fmz_433959_volatility_stop_flips"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


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


def _nmax(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else max(a, b)


def _nmin(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else min(a, b)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    n = int(p["length"])
    atr = tr.ewm(alpha=1 / n, adjust=False).mean()
    atr[np.arange(len(atr)) < n - 1] = np.nan          # Pine's atr() is undefined for its first n - 1 bars
    av, cv = atr.to_numpy(), c.to_numpy(dtype=float)
    k = float(p["mult"])
    m = len(cv)
    up = np.zeros(m, dtype=bool)
    mx = mn = vs = 0.0
    up_prev = True
    for i in range(m):
        mx1 = _nmax(0.0 if np.isnan(mx) else mx, cv[i])
        mn1 = _nmin(0.0 if np.isnan(mn) else mn, cv[i])
        stop = mx1 - k * av[i] if up_prev else mn1 + k * av[i]
        vprev = 0.0 if np.isnan(vs) else vs
        vs1 = _nmax(vprev, stop) if up_prev else _nmin(vprev, stop)
        is_up = bool(cv[i] - vs1 >= 0) if not np.isnan(vs1) else False
        changed = is_up != up_prev
        mx = cv[i] if changed else mx1
        mn = cv[i] if changed else mn1
        vs = ((mx - k * av[i]) if is_up else (mn + k * av[i])) if changed else vs1
        up[i] = is_up
        up_prev = is_up
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(up, index=ix), false, pd.Series(~up, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
