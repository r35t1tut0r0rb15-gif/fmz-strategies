"""SMA 55 reclaims on the cloud's side, daily bars: the close crossing over the SMA 55 while over both (undisplaced) spans and the SMA 200 goes long; crossing under it while under both spans and the SMA 200 goes short; reversing.
Port of FMZ strategy #451705 "Ichimoku Cloud and Moving Average Strategy" (Ichimoku Cloud and Moving Average Strategy (ICMA)).

FMZ source id: 451705

Source
    https://www.fmz.com/strategy/451705 (PineScript v5, FMZ last modified 2024-05-17 10:55:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-160), SMA 55 / 200; conversion 9, base 26, span B 52 (SMA of high + low); displacement 26 (unused)
    close > spanA and spanB and close > sma200 and close[1] < sma55 and close > sma55 -> entry Buy
    close < spanA and spanB and close < sma200 and close[1] > sma55 and close < sma55 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spans are taken at the current bar (the displacement input is never used). close[1] is
      compared with the current SMA 55, as written. There is no exit: positions end at the opposite
      entry. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA reclaims filtered by the cloud and the SMA 200.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451705_sma55_reclaim_cloud_sma200_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_ma": [55, 20],
    "long_ma": [200, 100],
}
DEFAULT_PARAMS = {"short_ma": 55, "long_ma": 200, "conv": 9, "base": 26, "span_b": 52}


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
    hl = h + lo
    conv = hl.rolling(int(p["conv"])).mean() / 2
    base = hl.rolling(int(p["base"])).mean() / 2
    span_a, span_b = (conv + base) / 2, hl.rolling(int(p["span_b"])).mean() / 2
    s55 = c.rolling(int(p["short_ma"])).mean()
    s200 = c.rolling(int(p["long_ma"])).mean()
    c1 = c.shift(1)
    le = (c > span_a) & (c > span_b) & (c > s200) & (c1 < s55) & (c > s55)
    se = (c < span_a) & (c < span_b) & (c < s200) & (c1 > s55) & (c < s55)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
