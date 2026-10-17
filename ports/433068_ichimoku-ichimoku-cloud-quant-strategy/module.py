"""Ichimoku cloud longs with an EMA filter, broker days, long only: with lead line 1 above lead line 2, the close above lead
line 1, a green candle and the EMA 24 above the EMA 90, a long opens from flat; a red candle closing below lead line 1
closes it.
Port of FMZ strategy #433068 "Ichimoku云图量化策略Ichimoku-Cloud-Quant-Strategy" (Ichimoku only Long Strategy).

FMZ source id: 433068

Source
    https://www.fmz.com/strategy/433068 (PineScript v4, FMZ last modified 2023-11-24 10:15:15).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 173-250), EMA filter on (24 / 90), stoch RSI off; conversion 9, base 26, lagging span 2 52, displacement 1
    lead1 = avg(donchian(9), donchian(26));  lead2 = donchian(52)  (both read on the current bar, unshifted)
    lead1 > lead2 and close > lead1 and close > open and ema(24) > ema(90) and opentrades < 1 -> entry long
    close < lead1 and close < open -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lead lines are compared on the current bar (the displacement only shifts the plot). The
      stochastic-RSI branch is off by default.
    * Long only; Opposite entries cannot occur. The date window is always true. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku lines, candle colour and EMA order.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433068_ichimoku_long_ema_filter"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema1": [24, 12],
    "ema2": [90, 50],
}
DEFAULT_PARAMS = {"ema1": 24, "ema2": 90, "conv": 9, "base": 26, "span2": 52}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))

    def don(n):
        return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2

    l1 = (don(p["conv"]) + don(p["base"])) / 2
    l2 = don(p["span2"])
    e1 = c.ewm(span=int(p["ema1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ema2"]), adjust=False).mean()
    ent = ((l1 > l2) & (c > l1) & (c > o) & (e1 > e2)).to_numpy()
    ex = ((c < l1) & (c < o)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 0 and ent[i]:
            pos = 1
        elif pos == 1 and ex[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
