"""Bollinger 55 breakouts with a structure shift and a momentum candle, broker days: the close crossing above the upper
band, above the SMA 55, above the previous swing-break high, on a candle whose body is at least 70 % of its range,
goes long; the mirror goes short; the close crossing back through the basis closes the trade.
Port of FMZ strategy #489975 "动量驱动型布林带突破与智能资金概念融合策略-Momentum-Driven-Bollinger-Breakout-with-Smart-Money-Concepts-Integration-Strategy" (02 SMC + BB Breakout v4 + Momentum Color).

FMZ source id: 489975

Source
    https://www.fmz.com/strategy/489975 (PineScript v6, FMZ last modified 2025-04-10 16:12:38).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 187-260), BB 55 x 2, swing 12, order block 20, body 70 %
    trend = security(ticker, '1D', close) > sma(that, 55)   (the chart is daily: the bar's own close vs the basis)
    previous_high = valuewhen(high > highest(high[1], 12), high[1], 0);  shift_bull = close > previous_high
    long = crossover(close, upper) and trend and shift_bull and body >= 70 % of range and close > open; short mirrored
    exit long = crossunder(close, basis) or close < lowest(low, 20) x 0.99;  exit short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The '1D' security on the daily chart is the bar's own close (complete at its close); its SMA 55 is the basis.
    * The order-block exits compare the close with the 20-bar extreme INCLUDING the current bar x 0.99 / 1.01, which
      can never be crossed: inert, as written (left out).
    * Closes are written after the entries: they act on the position held at the bar's start, never undoing an entry
      made on the bar (as #430850). Entries reverse (REVERSAL INTENDED).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bands, swing levels and candle proportions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 5 %-of-equity quantity quoted in original_sizing.txt.
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

NAME = "fmz_489975_bb55_breakout_structure_momentum"
FAMILY = "bollinger_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [55, 20],
    "body_pct": [0.7, 0.5],
}
DEFAULT_PARAMS = {"length": 55, "mult": 2.0, "swing_length": 12, "body_pct": 0.7}


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


def _valuewhen(cond, val):
    out = np.full(len(cond), np.nan)
    cur = np.nan
    for i in range(len(cond)):
        if cond[i]:
            cur = val[i]
        out[i] = cur
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = p["mult"] * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    s = int(p["swing_length"])
    prev_hi = _valuewhen((h > h.shift(1).rolling(s).max()).to_numpy(), h.shift(1).to_numpy())
    prev_lo = _valuewhen((lo < lo.shift(1).rolling(s).min()).to_numpy(), lo.shift(1).to_numpy())
    rng = h - lo
    body = ((c - o).abs() / rng).where(rng > 0, 0.0)
    trend = c > basis
    long_c = ((c > upper) & (c.shift(1) <= upper.shift(1)) & trend & (c > prev_hi)
              & (body >= p["body_pct"]) & (c > o)).to_numpy()
    short_c = ((c < lower) & (c.shift(1) >= lower.shift(1)) & ~trend & (c < prev_lo)
               & (body >= p["body_pct"]) & (c < o)).to_numpy()
    x_long = ((c < basis) & (c.shift(1) >= basis.shift(1))).to_numpy()
    x_short = ((c > basis) & (c.shift(1) <= basis.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if long_c[i]:
            pos = 1
        if short_c[i]:
            pos = -1
        if start == 1 and pos == 1 and x_long[i]:
            pos = 0
        if start == -1 and pos == -1 and x_short[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
