"""Supertrend 3 / 7 flips, broker days: the trend turning up goes long, turning down goes short; always in after the first
flip. The ATR bracket in the source never gets a level (see below), so there are no other exits.
Port of FMZ strategy #433946 "基于ATR和MA组合的超级趋势交易策略Supertrend-Trading-Strategy-Based-on-ATR-and-MA-Combination" (Supertrend V1.0 - Buy or Sell Signal).

FMZ source id: 433946

Source
    https://www.fmz.com/strategy/433946 (PineScript v3, FMZ last modified 2023-12-01 16:40:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 228-341), factor 3, period 7; ATR 14, stop factor 1.5, profit factor 1.0
    Up = hl2 - 3 atr(7), Dn = hl2 + 3 atr(7);  TrendUp / TrendDown ratchets;  Trend = close > TrendDown[1] ? 1 : close < TrendUp[1] ? -1 : Trend[1]
    Trend flips to 1 -> entry long;  flips to -1 -> entry short
    longStop = 1.5 x valuewhen(bought, Atr, 0) with bought = position_size > position_size (never true) -> exit(loss = na, profit = na)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written "bought" compares the position size with itself, so it is never true: the valuewhen
      stays undefined, the exits get no loss / profit and never fire. Only the flips trade.
    * strategy.entry reverses: REVERSAL INTENDED. The date window is open from 2016. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR trailing line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the decimal-scaled ATR bracket stored in original_sizing.txt.
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

NAME = "fmz_433946_supertrend_3_7_flips"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "pd": [7, 14],
}
DEFAULT_PARAMS = {"factor": 3.0, "pd": 7}


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
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / int(p["pd"]), adjust=False).mean()
    hl2 = (h + lo) / 2
    upv = (hl2 - float(p["factor"]) * atr).to_numpy()
    dnv = (hl2 + float(p["factor"]) * atr).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tu, td = np.zeros(m), np.zeros(m)
    trend = np.ones(m, dtype=np.int8)
    for i in range(m):
        tu_p = tu[i - 1] if i > 0 else 0.0
        td_p = td[i - 1] if i > 0 else 0.0
        c_p = cv[i - 1] if i > 0 else np.nan
        tu[i] = max(upv[i], tu_p) if c_p > tu_p else upv[i]
        td[i] = min(dnv[i], td_p) if c_p < td_p else dnv[i]
        tr_p = trend[i - 1] if i > 0 else 1
        trend[i] = 1 if cv[i] > td_p else (-1 if cv[i] < tu_p else tr_p)
    t1 = np.concatenate(([1], trend[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((trend == 1) & (t1 == -1), index=ix), false,
            pd.Series((trend == -1) & (t1 == 1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
