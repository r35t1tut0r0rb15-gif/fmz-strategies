"""HPotter close vs SMA of the daily close inside a 23:00-08:00 UTC window, 4-hour bars: a change of side (close
above / below the 14-bar SMA of the daily close) inside the window enters that side; outside the window
everything is closed.
Port of FMZ strategy #429383 "Dual Moving Average Reversal Trading Strategy" (Simple SMA Strategy Backtest).

FMZ source id: 429383

Source
    https://www.fmz.com/strategy/429383 (PineScript v4, FMZ last modified 2023-10-16 15:50:35).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 149-188), daily resolution, SMA 14, window "2300-0800" at 15-minute resolution, TP / SL off
    xSeries = security(tickerid, 'D', close); xSMA = sma(xSeries, 14)
    pos = close > xSMA ? 1 : close < xSMA ? -1 : pos[1]; possig = pos when it changes, else 0
    possig 1 / -1 and in window -> entry long / short; not in window -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * security('D', close) without lookahead is read as the last completed broker day's close
      (17:00 America/New_York), built inside simulate() from the port's own bars; the source's value on
      the last bar of a day already includes that day (one bar earlier): stated approximation. The SMA
      14 is taken over the chart's bars of that series, as written.
    * The window is read in exchange time, taken as UTC (FMZ crypto data; as #428812): a 4-hour bar is in
      it when its open time is inside 23:00-08:00 (the 00:00 and 04:00 bars).
    * UseTPSL defaults to false (stored). "Trade Reverse" defaults to false.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days.
    2 generic: PASS, price vs a moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the off-by-default TP / SL stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: ND429383 (2 members, best partner #440107, Jaccard 0.789); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: window 23:00-08:00 UTC (UTC, no DST; not a venue open); daily values on broker days (17:00 America/New_York).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429383_daily_close_sma_window"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 28],
}
DEFAULT_PARAMS = {"length": 14, "win_start": 1380, "win_end": 480}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    lab = broker_day(bars_df.index)
    dclose = c.groupby(lab).last().shift(1)                     # the last completed broker day
    xs = pd.Series(dclose.reindex(lab).to_numpy(), index=c.index)
    sma = xs.rolling(int(p["length"])).mean()
    upc, dnc = (c > sma).to_numpy(), (c < sma).to_numpy()
    m = len(c)
    pos = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if upc[i]:
            q = 1
        elif dnc[i]:
            q = -1
        pos[i] = q
    prevp = np.concatenate(([0], pos[:-1]))
    sig = np.where(prevp != pos, pos, 0)
    idx = bars_df.index.tz_convert("UTC")
    mins = np.asarray(idx.hour * 60 + idx.minute)
    in_win = (mins >= p["win_start"]) | (mins < p["win_end"])     # 23:00-08:00 crosses midnight
    tgt = np.zeros(m, dtype=np.int8)
    cur = 0
    for i in range(m):
        if in_win[i]:
            if sig[i] == 1:
                cur = 1
            elif sig[i] == -1:
                cur = -1
        else:
            cur = 0
        tgt[i] = cur
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
