"""Dominant green candles closing above a 5-bar high band, broker days, long only: a large green candle (small wicks, body beating the last three, opening above the previous close) closing above the
SMA 5 of highs goes long; the close under the SMA 5 of lows closes.
Port of FMZ strategy #441097 "5 Day Moving Average Channel Breakout Strategy Combined With Mileage Concept" (5MABAND + Mileage Concept Buy & Sell Strategy).

FMZ source id: 441097

Source
    https://www.fmz.com/strategy/441097 (PineScript v5, FMZ last modified 2024-02-05 15:16:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-156), band: SMA 5 of highs and of lows
    buy = mileage buy candle and close > avgHigh -> entry Buy;  close < avgLow -> close Buy (twice)
    sell = mileage sell candle (needs close > avgHigh) and close < avgLow -> entry Sell;  close < avgLow / close > avgHigh -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short entry needs the close above the high band and under the low band at once, which cannot
      happen (the high band is above the low band), so the script never sells short: ported long only. A
      close acts only on the held position. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle pattern and band tests.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441097_mileage_candle_5ma_band_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [5, 10],
}
DEFAULT_PARAMS = {"length": 5}


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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ah, al = h.rolling(n).mean(), lo.rolling(n).mean()
    gb = c - o
    buy = (c > o) & (h - c < gb) & (o - lo < gb) & (o > c.shift(1)) & (c > ah)
    for k in (1, 2, 3):
        buy &= gb > gb.shift(k)
    buy = buy.to_numpy()
    xb = (c < al).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = 0
    for i in range(m):
        if held == 1 and xb[i]:
            lx[i], held = True, 0
        elif held == 0 and buy[i] and i + 1 < m:
            le[i], held = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
