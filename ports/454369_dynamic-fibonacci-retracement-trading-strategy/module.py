"""Pullbacks to an averaged 50 % retracement in an uptrend, daily bars, long only: with the close over the SMA 200 and SMA 50, a close at or under the average midpoint of the 9 / 21 / 50-bar ranges buys. The exit bracket re-sent every bar from the moving 78.6 % level is not ported (pending), so the port has no exit.
Port of FMZ strategy #454369 "Dynamic Fibonacci Retracement Trading Strategy" (50% Retracement Strategy).

FMZ source id: 454369

Source
    https://www.fmz.com/strategy/454369 (PineScript v5, FMZ last modified 2024-06-17 17:02:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 106-160), SMA 200 / 50; ranges 9 / 21 / 50; stop at the averaged 78.6 % level, target 2R from the average price (every bar)
    close > sma200 and sma50 -> fib50 = mean of the three range midpoints, fib786 from the three ranges (var);  same and close <= fib50 -> entry Long
    every bar: exit(limit = avg + (avg - fib786) x 2, stop = fib786)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The retracement levels are recomputed on every bar of the uptrend and kept otherwise (var). The
      bracket is re-sent on every bar from the current 78.6 % level and the average price, so it moves
      while the trade is on; stops() cannot express this: it is not ported and the module gets the mark
      trailing_stop_pending (as #437800, #438034). Without it the port has no exit (one long held from
      the first signal), as #451391. Long only. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket pending (mark).
    2 generic: PASS, retracement pullbacks in an uptrend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_454369_averaged_50pct_retracement_pullback_long"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len_200": [200, 100],
    "len_50": [50, 30],
}
DEFAULT_PARAMS = {"len_200": 200, "len_50": 50, "len_21": 21, "len_9": 9}


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
    ma200 = c.rolling(int(p["len_200"])).mean()
    ma50 = c.rolling(int(p["len_50"])).mean()
    up = ((c > ma200) & (c > ma50)).to_numpy()
    mids = [(h.rolling(int(p[k])).max() + lo.rolling(int(p[k])).min()) / 2 for k in ("len_21", "len_50", "len_9")]
    mid = (sum(mids) / 3).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    fib = np.full(m, np.nan)
    keep = np.nan
    for i in range(m):
        if up[i]:
            keep = mid[i]                    # var level, recomputed only in the uptrend
        fib[i] = keep
    with np.errstate(invalid="ignore"):
        le = up & (cv <= fib)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
