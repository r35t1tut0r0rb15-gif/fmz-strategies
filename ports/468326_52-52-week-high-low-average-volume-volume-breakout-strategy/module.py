"""Broker days, long only: a close within 10 % of the 260-bar closing high on volume above 1.5 x its 50-bar average, on a day whose open-to-close change is at most 3 %, goes long; nothing ever closes it (held to the end of the data, as written).
Port of FMZ strategy #468326 "52周高低位-平均成交量-成交量突破策略-52-Week-High-Low-Average-Volume-Volume-Breakout-Strategy" (Custom Stock Trading Strategy with 50-Day Average Volume).

FMZ source id: 468326

Source
    https://www.fmz.com/strategy/468326 (PineScript v5, FMZ last modified 2024-09-26 15:47:03).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 148-210), 52 weeks x 5 days = 260 bars; volume SMA 50 x 1.5; daily change <= 3 % (10 % on weekly / monthly charts)
    percentFromHighValue = 100 x (highest(close, 260) - close) / highest(close, 260)
    entryCondition = percentFromHighValue <= 10 and volume > sma(volume, 50) x 1.5 and 100 x (close - open) / open <= 3 -> entry Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script has no exit of any kind: the first qualifying day opens a long held to the end of the
      data, as written (as #458234). The 3 % limit applies on daily bars (the 10 % branch is for weekly
      or monthly charts); any down day passes it. The "52-week high" is the highest CLOSE of 260 bars.
      Long only. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, near-high volume breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.5 x its SMA 50; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_468326_near_52w_high_volume_rise_no_exit_long_only"
FAMILY = "breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pct_from_high": [10.0, 5.0],
    "vol_mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"pct_from_high": 10.0, "vol_mult": 1.5, "length": 260, "vol_len": 50, "chg_limit": 3.0}


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
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    hh = c.rolling(int(p["length"])).max()
    near = 100 * (hh - c) / hh <= float(p["pct_from_high"])
    vol_ok = v > v.rolling(int(p["vol_len"])).mean() * float(p["vol_mult"])
    chg_ok = 100 * (c - o) / o <= float(p["chg_limit"])
    entry = near & vol_ok & chg_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return entry.astype(bool), false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
