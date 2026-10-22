"""EMA 89 / 200 and price-channel trend starts, 1-hour bars, 00:00-16:00 UTC: the trend state turning from neutral to up (EMA 89 above EMA 200 and the EMA 34 of the lows above it) goes long, to down
short; a 0.32 % target and a 0.1 % stop from the entry; the neutral state or the end of the window closes.
Port of FMZ strategy #440505 "Trend Trading Strategy Based on Price Channel of Double Moving Averages" (Trend trader Strategy).

FMZ source id: 440505

Source
    https://www.fmz.com/strategy/440505 (PineScript v4, FMZ last modified 2024-01-31 10:37:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-411), PAC 34; EMA 89 / 200 / 600; DST 1 (window 2400-1600); tp 0.0032, sl 0.001 (as close x / mintick); date window 2020
    TrendDirection = ema89 > ema200 and ema(low, 34) > ema200 ? 1 : ema89 < ema200 and ema(high, 34) < ema200 ? -1 : 0;  red after yellow and c_time -> entry short;  green after yellow and c_time -> entry long
    strategy.exit(profit = close tp / mintick, loss = close sl / mintick) each side;  yellow or not c_time -> close short and long

Interpretation choices (Pine rules in SURVEY_README.md)
    * c_time is the bar's open inside 24:00-16:00, read on the UTC bar open: bars opening 00:00-15:00.
      The date window only feeds an unused condition and is dropped; the trail-stop block and the HA
      option are off. The bracket is in ticks from the entry, re-sized from the close: fixed fractions of
      the entry (as #437751), target 0.0032 and stop 0.001. A trade starts only after a neutral bar,
      which closes any position, so trades start from flat: Opposite entries cannot occur (entries only
      from flat). Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick bracket from the close -> fixed fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entries on bars opening 00:00-15:00 UTC; close outside (bar open time).
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440505_pac_ema_trend_start_bracket"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.0032, 0.01],
    "sl": [0.001, 0.005],
}
DEFAULT_PARAMS = {"tp": 0.0032, "sl": 0.001, "pac": 34, "fast": 89, "medium": 200, "win_end": 16}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    fe = c.ewm(span=int(p["fast"]), adjust=False).mean()
    me = c.ewm(span=int(p["medium"]), adjust=False).mean()
    n = int(p["pac"])
    pl = lo.ewm(span=n, adjust=False).mean()
    pu = h.ewm(span=n, adjust=False).mean()
    td = pd.Series(np.where((fe > me) & (pl > me), 1, np.where((fe < me) & (pu < me), -1, 0)), index=c.index)
    hour = bars_df.index.tz_convert("UTC").hour
    ctime = pd.Series(hour < int(p["win_end"]), index=c.index)
    prev0 = td.shift(1) == 0
    long_ = (td == 1) & prev0 & ctime
    short_ = (td == -1) & prev0 & ctime
    out = (td == 0) | ~ctime
    return long_, out, short_, out.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
