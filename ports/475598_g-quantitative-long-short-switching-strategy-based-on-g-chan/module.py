"""G-Channel state against the EMA 50, daily bars, long only: while the channel state is bullish with the close under the EMA 50 it buys; while bearish with the close over it, it sells.
Port of FMZ strategy #475598 "基于G通道和指数移动平均的量化多空转换策略-Quantitative-Long-Short-Switching-Strategy-Based-on-G-Channel-and-EMA" (G-Channel with EMA Strategy).

FMZ source id: 475598

Source
    https://www.fmz.com/strategy/475598 (PineScript v5, FMZ last modified 2024-12-20 14:31:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-145), G-Channel 100; EMA 50
    a := max(src, nz(a[1])) - nz(a[1] - b[1]) / 100;  b := min(src, nz(b[1])) + nz(a[1] - b[1]) / 100;  crossup = b[1] < close[1] and b > close;  crossdn = a[1] < close[1] and a > close;  bullish = barssince(crossdn) <= barssince(crossup);  bullish and close < ema -> entry Buy;  not bullish and close > ema -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel is the source's recursion from nz seeds of 0 (a loop) with the cross tests as written
      (as #474864). barssince is na before the first cross and a comparison with na is false, so "not
      bullish" holds until both crosses have happened. The entry and close cannot hold on one bar. Long
      only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, G-Channel state against an EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_475598_g_channel100_ema50_state_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50],
    "ema_length": [50, 100],
}
DEFAULT_PARAMS = {"length": 100, "ema_length": 50}


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


def _barssince(k):
    out = np.full(len(k), np.nan)
    last = -1
    for i in range(len(k)):
        if k[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    cv = c.to_numpy(dtype=float)
    n = float(p["length"])
    av, bv = np.zeros(len(cv)), np.zeros(len(cv))
    a1 = b1 = 0.0
    for i in range(len(cv)):
        a = max(cv[i], a1) - (a1 - b1) / n
        b = min(cv[i], b1) + (a1 - b1) / n
        av[i], bv[i] = a, b
        a1, b1 = a, b
    cu = np.zeros(len(cv), dtype=bool)
    cd = np.zeros(len(cv), dtype=bool)
    cu[1:] = (bv[:-1] < cv[:-1]) & (bv[1:] > cv[1:])
    cd[1:] = (av[:-1] < cv[:-1]) & (av[1:] > cv[1:])
    bull = pd.Series(_barssince(cd) <= _barssince(cu), index=c.index)   # na compares false
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    le = bull & (c < e)
    lx = ~bull & (c > e)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
