"""EMA 9 / 21 crosses with a close-checked 1 % trail, broker days: EMA 9 crossing above EMA 21 goes long, crossing
below goes short; a close more than 1 % below the highest close since the signal closes the long (shorts mirrored).
Port of FMZ strategy #491505 "指数移动平均线交叉动态跟踪止损策略-EMA-Crossover-Dynamic-Trailing-Stop-Loss-Strategy" (EMA Crossover Strategy with Trailing Stop and Alerts).

FMZ source id: 491505

Source
    https://www.fmz.com/strategy/491505 (PineScript v6, FMZ last modified 2025-04-21 15:53:17).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 182-237), EMA 9 / 21, trail 1 %
    buy = crossover(ema9, ema21) -> highestPrice = close;  sell = crossunder -> lowestPrice = close
    long held: highestPrice = max(highestPrice, close); close < highestPrice x 0.99 -> close "Buy" (shorts mirrored)
    then entry long on buy, short on sell (strategy.entry reverses)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail is checked on bar closes: a close-based exit signal (rule 2 / 3), not a stop; no mark.
    * Source order on each bar: the reference resets, the trail checks (on the position held at the bar, i.e. filled
      from the bar after the signal), then the entries. A trail close and an opposite entry on one bar are one
      reversal.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a close-checked trail.
    2 generic: PASS, EMAs and a percentage.
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

NAME = "fmz_491505_ema_9_21_cross_close_trail"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trail_pct": [1.0, 3.0],
    "ema_long": [21, 50],
}
DEFAULT_PARAMS = {"ema_short": 9, "ema_long": 21, "trail_pct": 1.0}


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
    e1 = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    buy = ((e1 > e2) & (e1.shift(1) <= e2.shift(1))).to_numpy()
    sell = ((e1 < e2) & (e1.shift(1) >= e2.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    k = p["trail_pct"] / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, held, hi, lo = 0, 0, np.nan, np.nan
    for i in range(m):
        if buy[i]:
            hi = cv[i]
        if sell[i]:
            lo = cv[i]
        if held == 1:
            hi = max(hi, cv[i])
            if cv[i] < hi * (1 - k):
                pos = 0
        if held == -1:
            lo = min(lo, cv[i])
            if cv[i] > lo * (1 + k):
                pos = 0
        if buy[i]:
            pos = 1
        if sell[i]:
            pos = -1
        tgt[i] = pos
        held = pos                              # position held at the next bar (filled at its open)
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
