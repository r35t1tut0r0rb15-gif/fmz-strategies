"""Supertrend crosses on the EMA 34 side, broker days, as written with the built-in Supertrend's arguments swapped (factor
10, ATR 2): a close crossing above the line with the close above the EMA goes long, closed by a cross back under or a
close under the EMA; the short mirror.
Port of FMZ strategy #434997 "EMA与SuperTrend组合趋势跟踪策略EMA-and-SuperTrend-Combined-Trend-Following-Strategy" (EMA SuperTrend Strategy).

FMZ source id: 434997

Source
    https://www.fmz.com/strategy/434997 (PineScript v5, FMZ last modified 2023-12-11 15:49:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 173-214), ta.supertrend(length = 10, int(mult) = 2) -> factor 10, ATR 2; EMA 34
    longEntry = crossover(close, supertrend) and close > ema34;  longExit = crossunder(close, supertrend) or close < ema34
    shortEntry = crossunder(close, supertrend) and close < ema34;  shortExit = crossover(close, supertrend) or close > ema34

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend(factor, atrPeriod) receives (10, 2): a factor of 10 on a 2-bar ATR, as written
      (the intended 2 x ATR 10 is owed). The closes act on the position held on the bar; an entry on
      the same bar wins. strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bands and an average side.
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

NAME = "fmz_434997_supertrend_swapped_ema34"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [10.0, 2.0],
    "atr_len": [2, 10],
}
DEFAULT_PARAMS = {"factor": 10.0, "atr_len": 2, "ema_len": 34}


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


def _supertrend(h, lo, c, factor, n):
    """Pine's built-in supertrend(factor, atrPeriod): the line."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif st[i - 1] == ub[i - 1]:
            d = -1 if cv[i] > ub[i] else 1
        else:
            d = 1 if cv[i] < lb[i] else -1
        st[i] = lb[i] if d == -1 else ub[i]
    return st


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    st = _supertrend(h, lo, c, float(p["factor"]), int(p["atr_len"]))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    c1, s1 = np.concatenate(([np.nan], cv[:-1])), np.concatenate(([np.nan], st[:-1]))
    with np.errstate(invalid="ignore"):
        xo, xu = (cv > st) & (c1 <= s1), (cv < st) & (c1 >= s1)
        lc, sc = xo & (cv > ema), xu & (cv < ema)
        xl, xs = xu | (cv < ema), xo | (cv > ema)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if pos == 1 and xl[i]:
            new = 0
        if pos == -1 and xs[i]:
            new = 0
        if lc[i]:
            new = 1
        if sc[i]:
            new = -1
        tgt[i] = new
        pos = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
