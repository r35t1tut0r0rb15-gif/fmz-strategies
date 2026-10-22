"""Turtle 20-bar channel touches, daily bars: the high reaching the previous 20-bar high goes long, the low reaching the previous 20-bar low goes short (each only after an earlier opposite touch, not on the
previous bar); reversing (the exit calls carry no exit price and never act).
Port of FMZ strategy #443136 "Adaptive Channel Breakout Strategy" (Turtle Trade Channels Strategy (TTCS)).

FMZ source id: 443136

Source
    https://www.fmz.com/strategy/443136 (PineScript v4, FMZ last modified 2024-02-29 14:49:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 125-157), entry length 20, exit length 10; 100 % of equity
    buy = high == upper[1] or crossover(high, upper[1]);  sell = low == lower[1] or crossover(lower[1], low)
    buy and barssince(buy) < barssince(sell[1]) -> entry Buy;  sell and barssince(sell) < barssince(buy[1]) -> entry Sell;  exit(from_entry, when = ...) with no stop / limit / trail

Interpretation choices (Pine rules in SURVEY_README.md)
    * barssince(buy) is 0 on a signal bar, so an entry needs the opposite signal somewhere before the
      previous bar (and not on it), as written. The strategy.exit calls give no profit, loss, stop, limit
      or trail, so they place nothing: positions end at the opposite entry. lowest / highest with one
      argument use the low / high. strategy.entry reverses: REVERSAL INTENDED. The 100 % of equity size
      is sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel touches with an alternation test.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443136_turtle_channel_touch_alternating_reversal"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 55],
}
DEFAULT_PARAMS = {"length": 20}


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


def _since(flag):
    out = np.full(len(flag), np.nan)
    last = -1
    for i, f in enumerate(flag):
        if f:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo = bars_df["high"], bars_df["low"]
    n = int(p["length"])
    up1 = h.rolling(n).max().shift(1)
    dn1 = lo.rolling(n).min().shift(1)
    buy = ((h == up1) | ((h > up1) & (h.shift(1) <= up1.shift(1)))).to_numpy()
    sell = ((lo == dn1) | ((lo < dn1) & (lo.shift(1) >= dn1.shift(1)))).to_numpy()
    sb, ss = _since(buy), _since(sell)
    sb1 = _since(np.concatenate(([False], buy[:-1])))
    ss1 = _since(np.concatenate(([False], sell[:-1])))
    with np.errstate(invalid="ignore"):
        le = buy & (sb < ss1)
        se = sell & (ss < sb1)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le & ~se, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
