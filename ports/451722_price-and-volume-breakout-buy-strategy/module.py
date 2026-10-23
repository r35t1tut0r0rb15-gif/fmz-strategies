"""Broker days, long only: from flat, a close above the previous 60-bar high on volume above the previous 60-bar volume high with the close above the SMA 200 goes long; five closes in a row under the SMA 200 close it.
Port of FMZ strategy #451722 "Price and Volume Breakout Buy Strategy" (Price and Volume Breakout Buy Strategy [TradeDots]).

FMZ source id: 451722

Source
    https://www.fmz.com/strategy/451722 (PineScript v5, FMZ last modified 2024-05-17 14:54:13).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 97-128), price breakout 60; volume breakout 60; trendline SMA 200; order direction Long
    close > highest(60)[1] and volume > highest(volume, 60)[1] and close > sma(close, 200) and opentrades == 0 -> entry Long
    close and close[1 .. 4] all < sma(close, 200) (the current SMA) and long -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.highest(60) is the 60-bar high of the high. The five-close test compares each of the last five
      closes with the current SMA 200, as written. The direction input is Long, so the short branch never
      fires. Long only. 70 % of equity and the commission are sizing and costs. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price and volume range breakouts above the long trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 70 % of equity, capital 10000, commission 0.01 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its previous 60-bar high; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451722_price_volume_60bar_breakout_sma200_long_only"
FAMILY = "momentum_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "breakout": [60, 20],
    "trend_len": [200, 100],
}
DEFAULT_PARAMS = {"breakout": 60, "trend_len": 200}


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
    h, c, v = bars_df["high"], bars_df["close"], bars_df["volume"]
    n = int(p["breakout"])
    sma = c.rolling(int(p["trend_len"])).mean()
    buy = ((c > h.rolling(n).max().shift(1)) & (v > v.rolling(n).max().shift(1)) & (c > sma)).to_numpy()
    under = c < sma
    for k in range(1, 5):
        under = under & (c.shift(k) < sma)
    sell = under.to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and sell[i]:
            lx[i], pos = True, 0
        elif pos == 0 and buy[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
