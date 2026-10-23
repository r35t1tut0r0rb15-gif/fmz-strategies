"""Broker days, long only: a close above the 27-bar high of the bars ending 10 bars ago, on volume above 1.4 x its 27-day average, goes long; a close below the middle of that lagged channel closes it.
Port of FMZ strategy #478689 "基于多重条件的Donchian通道动量突破策略-Multi-Condition-Donchian-Channel-Momentum-Breakout-Strategy" (Breakout Strategy (lagged Donchian)).

FMZ source id: 478689

Source
    https://www.fmz.com/strategy/478689 (PineScript v6, FMZ last modified 2025-01-17 14:28:22).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 104-148), Donchian 27, offset 10; volume SMA 27 x 1.4; exit band Mid; 100 % of equity
    upper_band = highest(high[10], 27);  lower_band = lowest(low[10], 27);  long_condition = close > upper_band and volume > sma(volume, 27) x 1.4 -> entry Breakout Long
    close < (upper_band + lower_band) / 2 -> close Breakout Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel is shifted 10 bars back, as written. A close above the upper band is above the middle,
      so the entry and the close never meet on one bar; an entry while long adds nothing. The date inputs
      span all data. Long only. 100 % of equity and the commission are sizing and costs. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, lagged Donchian breakouts on volume, mid-channel exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, capital and commission stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.4 x its SMA 27; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_478689_lagged_donchian27_breakout_volume_mid_exit_long_only"
FAMILY = "channel_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [27, 20],
    "lag": [10, 0],
}
DEFAULT_PARAMS = {"length": 27, "lag": 10, "vol_mult": 1.4}


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
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    n, lag = int(p["length"]), int(p["lag"])
    up = h.shift(lag).rolling(n).max()
    dn = lo.shift(lag).rolling(n).min()
    mid = (up + dn) / 2
    entry = (c > up) & (v > v.rolling(n).mean() * float(p["vol_mult"]))
    ex = c < mid
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return entry.astype(bool), ex.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
