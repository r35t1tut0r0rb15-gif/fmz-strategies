"""HiLo channel midpoint crosses with an ADX filter, broker days: the close crossing over the 14-bar high / low midpoint with the ADX over
25 and +DI over 50 goes long; crossing under with the ADX over 25 and -DI over 50 goes short (reversing).
Port of FMZ strategy #435709 "Momentum Breakout Bi directional Tracking Strategy" (HiLo Activator with ADX).

FMZ source id: 435709

Source
    https://www.fmz.com/strategy/435709 (PineScript v4, FMZ last modified 2023-12-18 10:47:46).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 145-194), HiLo 14, ADX 14 (SMA smoothing), ADX threshold 25, DI threshold 50
    ha = (highest(high, 14) + lowest(low, 14)) / 2;  tr = max(high - high[1], low[1] - low) (not the true range);  atr = sma(tr, 14);  +DM / -DM as written, sma 14;  di = 100 sma(dm) / atr;  adx = sma(100 |di+ - di-| / (di+ + di-), 14)
    signalLong = crossover(close, ha) and adx > 25 and di_plus > 50;  signalShort = crossunder(close, ha) and adx > 25 and di_minus > 50;  entry / close of the opposite side on each signal

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "true range" is max(high - high[1], low[1] - low), as written, and every smoothing is a
      simple average. A zero denominator gives no signal. The backtest-data helper (a security call
      that is never used by the orders) is ignored. The opposite signal closes and opens the other side:
      REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel midpoint and a directional index.
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

NAME = "fmz_435709_hilo_adx_breakout"
FAMILY = "trend_confluence"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_ha": [14, 20],
    "adx_threshold": [25, 20],
}
DEFAULT_PARAMS = {"length_ha": 14, "adx_length": 14, "adx_threshold": 25, "di_threshold": 50}


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
    ha = (h.rolling(int(p["length_ha"])).max() + lo.rolling(int(p["length_ha"])).min()) / 2
    n = int(p["adx_length"])
    trh, trl = h - h.shift(1), lo.shift(1) - lo
    tr = pd.concat([trh, trl], axis=1).max(axis=1).where(trh.notna())
    atr = tr.rolling(n).mean()
    plus_dm = pd.Series(np.where(trh > trl, np.maximum(trh, 0), 0.0), index=c.index).where(trh.notna())
    minus_dm = pd.Series(np.where(trl > trh, np.maximum(trl, 0), 0.0), index=c.index).where(trh.notna())
    with np.errstate(invalid="ignore", divide="ignore"):
        di_plus = 100 * (plus_dm.rolling(n).mean() / atr)
        di_minus = 100 * (minus_dm.rolling(n).mean() / atr)
        dx = 100 * (di_plus - di_minus).abs() / (di_plus + di_minus)
    adx = dx.rolling(n).mean()
    th, dth = float(p["adx_threshold"]), float(p["di_threshold"])
    sl = ((c > ha) & (c.shift(1) <= ha.shift(1)) & (adx > th) & (di_plus > dth)).fillna(False).astype(bool)
    ss = ((c < ha) & (c.shift(1) >= ha.shift(1)) & (adx > th) & (di_minus > dth)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return sl, false, ss, false.copy()


def portfolio_kwargs(**params):
    return {}
