"""Closing breakouts in quiet ranges, daily bars: a close at the 9-bar highest close while the 5-bar average range is not above the 20-bar average goes long, a close at the 50-bar lowest close short; ten
bars after the fill the position closes; reversing.
Port of FMZ strategy #443239 "The Breakout Regression Strategy" (Crudeoil Breakout strategy).

FMZ source id: 443239

Source
    https://www.fmz.com/strategy/443239 (PineScript v5, FMZ last modified 2024-03-01 11:58:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-158), highest close 9; lowest close 50; exit after 10 bars; qty 1, capital 20000
    longCondition = close == highest(close, 9) and not (sma(range, 5) > sma(range, 20)) -> entry long;  shortCondition = close == lowest(close, 50) and not rangeFilter -> entry short
    longsince counts bars held long (0 when not long);  longsince >= 10 -> close long;  shorts mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The counters run on the bars a position is held, from 1 on the fill bar, so the close is sent on
      the tenth held bar. Ported in call order with one position at a time. strategy.entry reverses:
      REVERSAL INTENDED. The fixed quantity and capital are sizing. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, closing breakouts with a range filter; bar-count exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443239_quiet_range_close_breakout_ten_bar_exit"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "high_lookback": [9, 20],
    "exit_after": [10, 5],
}
DEFAULT_PARAMS = {"high_lookback": 9, "exit_after": 10, "low_lookback": 50}


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
    rng = h - lo
    wide = rng.rolling(5).mean() > rng.rolling(20).mean()
    lg = ((c == c.rolling(int(p["high_lookback"])).max()) & ~wide).to_numpy()
    sh = ((c == c.rolling(int(p["low_lookback"])).min()) & ~wide).to_numpy()
    k = int(p["exit_after"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held, ls, ss = 0, 0, 0
    for i in range(m):
        new = held
        if lg[i] and new != 1:
            new = 1
        if sh[i] and new != -1:
            new = -1
        ls = ls + 1 if held == 1 else 0
        ss = ss + 1 if held == -1 else 0
        if ls >= k and held == 1 and new == 1:
            new = 0
        if ss >= k and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
