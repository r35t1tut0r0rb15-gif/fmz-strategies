"""Broker days: the close above the SMA 200, SMA 50 above SMA 90, the high above its last two highs, the SMA 200 above its last two values and the MACD (12 / 26 / 9) of the price-volume trend above its signal goes long; the PVT MACD under its signal with the low under its last two lows on a down bar below the previous close goes short; reversing.
Port of FMZ strategy #442213 "Accumulation Stage Identifier and Trading Strategy" (Accumulate (stocktechbot)).

FMZ source id: 442213

Source
    https://www.fmz.com/strategy/442213 (PineScript v5, FMZ last modified 2024-02-20 11:29:57).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 112-218), SMA 200 / 50 / 90 / 21; MACD 12 / 26 / 9 of ta.pvt; lookback 21
    allup = close > sma200 and sma50 > sma90 and rising(high, 2) and rising(sma200, 2) and macd(pvt) > signal -> entry long
    alldwn = macd(pvt) < signal and falling(low, 2) and close < close[1] and close < open -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * rising(x, 2) is x above both of its last two values (falling likewise). ta.pvt = cumulative
      change / previous close x volume. The other inputs (OBV smoothing, ATR, the 30 % / 10 % range tests,
      the entry / exit lines) feed nothing. Entries repeat while their conditions hold and add nothing.
      When both fire on one bar the later call (short) wins. REVERSAL INTENDED. No sizing code. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, trend stack with a PVT MACD confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the price-volume trend feeding the MACD; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442213_sma_stack_pvt_macd_accumulation_reversal"
FAMILY = "volume_flow"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 50],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    pvt = (c.diff() / c.shift(1) * v).fillna(0.0).cumsum()
    macd = pvt.ewm(span=int(p["fast"]), adjust=False).mean() - pvt.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    s200, s50, s90 = c.rolling(200).mean(), c.rolling(50).mean(), c.rolling(90).mean()
    rise_h = h > pd.concat([h.shift(1), h.shift(2)], axis=1).max(axis=1, skipna=False)
    rise_200 = s200 > pd.concat([s200.shift(1), s200.shift(2)], axis=1).max(axis=1, skipna=False)
    fall_l = lo < pd.concat([lo.shift(1), lo.shift(2)], axis=1).min(axis=1, skipna=False)
    up = (c > s200) & (s50 > s90) & rise_h & rise_200 & (macd > sig)
    dn = (macd < sig) & fall_l & (c < c.shift(1)) & (c < o)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (up & ~dn).astype(bool), false, dn.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
