"""Distance-from-average "liquidation" extremes, long only, daily (broker-day) bars: once three 89-bar lows of the
close's distance from the SMA 15 / EMA 30 average have occurred, every bar is a buy signal; a held long is closed while
the distance is above -1 % or on an 89-bar high of the distance.
Port of FMZ strategy #483051 "动态流动性级联捕捉策略-Dynamic-Liquidity-Cascade-Capture-Strategy" (Liquidation Cascade Strategy).

FMZ source id: 483051

Source
    https://www.fmz.com/strategy/483051 (PineScript v5, FMZ last modified 2025-02-24 15:16:23).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 106-163), SMA 15, EMA 30, window 89, ATR 14
    dist = (close - avg) / avg x 100, avg = (sma15 + ema30) / 2
    shortLiq = dist is the 89-bar highest and > 0; longLiq = dist is the 89-bar lowest and < 0
    buy = valuewhen(longLiq, longLiq, 0) and valuewhen(..., 1) and valuewhen(..., 2) -> entry long; positionOpen
    close when positionOpen and (dist > -1 or shortLiq or close < close - 2 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * valuewhen of longLiq on longLiq bars is always true once it exists, so buy is "at least three longLiq bars so
      far": true on every bar after the third, as written.
    * close < close - 2 ATR can never hold (ATR > 0): inert. The close acts on the position held at the bar's start
      and never undoes that bar's entry (as #430850); with buy true on every bar the strategy alternates (in, then
      out while dist > -1), as written. Target-position state machine, exits only on going flat.
    * Long only; the source has no shorts. No stops. Daily bars are broker days (17:00 America/New_York) stamped with
      their first minute (as #430984). FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, distance from moving averages in percent and rolling extremes.
    3 crypto-exchange-only: no (exchange pair in the header only; "liquidation" is a name, no exchange data).
    4 signals only: no sizing in the source (strategy() defaults).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483051_distance_extreme_cascade_long"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "window": [89, 55],
    "exit_level": [-1.0, 0.0],
}
DEFAULT_PARAMS = {"sma_len": 15, "ema_len": 30, "window": 89, "exit_level": -1.0}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    avg = (c.rolling(int(p["sma_len"])).mean() + c.ewm(span=int(p["ema_len"]), adjust=False).mean()) / 2
    dist = (c - avg) / avg * 100
    w = int(p["window"])
    short_liq = ((dist == dist.rolling(w).max()) & (dist > 0)).to_numpy()
    long_liq = ((dist == dist.rolling(w).min()) & (dist < 0)).to_numpy()
    buy = np.cumsum(long_liq) >= 3
    above = (dist > p["exit_level"]).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos, flag = 0, False
    for i in range(m):
        start = pos
        if buy[i]:
            pos, flag = 1, True
        if flag and (above[i] or short_liq[i]):
            if start == 1 and pos == 1:
                pos = 0
            flag = False
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
