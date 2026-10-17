"""Tenkan above kijun over the EMA 200, broker days, long only: while the conversion line 9 is above the base line 26 and
the close is above the EMA 200 the strategy goes long; the conversion line falling below the base line closes it.
Port of FMZ strategy #433433 "Trend Following Strategy Based on Moving Averages" (TK Cross > EMA200 Strat).

FMZ source id: 433433

Source
    https://www.fmz.com/strategy/433433 (PineScript v3, FMZ last modified 2023-11-27 15:57:15).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 121-148), conversion 9, base 26, EMA 200 (span 2 52 and displacement 26 are plots)
    entry long (qty initial_capital / close) when conversion > base and close > ema200;  close when conversion < base

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry is a level: it re-fires every bar the condition holds (ignored while long, pyramiding
      1). The parabolic SAR lines are plots only; the quantity is sizing.
    * Long only; Opposite entries cannot occur. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku lines and an EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the initial_capital / close quantity stored in original_sizing.txt.
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

NAME = "fmz_433433_tk_cross_above_ema200"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conv": [9, 20],
    "ema_len": [200, 100],
}
DEFAULT_PARAMS = {"conv": 9, "base": 26, "ema_len": 200}


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

    def don(n):
        return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2

    cv, bs = don(p["conv"]), don(p["base"])
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    ent = ((cv > bs) & (c > e)).to_numpy()
    ex = (cv < bs).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 1 and ex[i]:
            pos = 0
        elif pos == 0 and ent[i]:
            pos = 1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
