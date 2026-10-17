"""First-candle breakout with a close-checked trail of 1.5 ranges and an end-of-day close, 1-minute bars: the 09:15
candle's high and low are recorded; from 10:00 the first close above the high goes long (below the low goes short),
one trade a day; a trail 1.5 x the first candle's range behind the best close closes it (checked on closes), and
everything closes at 15:30.
Port of FMZ strategy #489018 "首个蜡烛突破-动态追踪止损与收盘平仓策略-First-Candle-Breakout-Dynamic-Trailing-Stop-EOD-Close-Strategy" (First Candle Breakout - Trailing Stop & EOD Close).

FMZ source id: 489018

Source
    https://www.fmz.com/strategy/489018 (PineScript v5, FMZ last modified 2025-04-01 11:06:47).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 164-221), first candle 09:15, end 15:30 (exchange time), trail 1.5 x range
    the 09:15 bar sets firstHigh / firstLow, resets tradeTaken, the direction and the trail
    long = close > firstHigh and not tradeTaken and hour > 9 -> entry long, trail = close - 1.5 x range (short mirrored)
    long: trail = max(trail, close - 1.5 x range); close <= trail -> close;  tradeTaken and 15:30 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail is checked on closes: a close-based exit signal (rule 2 / 3), no mark.
    * Session open (check 9 / C6): 09:15 and 15:30 in the chart's time zone: UTC on the author's Binance chart
      (session_tz "UTC", the default) or the evident NSE session in Asia/Kolkata (no DST), the grid's second reading;
      entries from 10:00 local ("hour > 9"). As #489035.
    * The 15:30 close_all is written last and leaves the bar flat (desktop convention). One trade a day.
    * Entries reverse only if a trade survived to another day (REVERSAL INTENDED). FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and close-checked exits.
    2 generic: PASS, the first candle's range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 09:15 first candle and 15:30 close in session_tz (UTC as written; Asia/Kolkata, no DST, as the variant).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489018_first_candle_breakout_close_trail_eod"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "session_tz": ["UTC", "Asia/Kolkata"],
    "trail_mult": [1.5, 1.0],
}
DEFAULT_PARAMS = {"session_tz": "UTC", "start_hour": 9, "start_minute": 15, "end_hour": 15, "end_minute": 30,
                  "trail_mult": 1.5}


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
    loc = bars_df.index.tz_convert(p["session_tz"])
    hr, mn = loc.hour.to_numpy(), loc.minute.to_numpy()
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    sh, sm, eh, em = (int(p[k]) for k in ("start_hour", "start_minute", "end_hour", "end_minute"))
    k = float(p["trail_mult"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos, fh, fl, taken, direction, trail = 0, np.nan, np.nan, False, 0, np.nan
    for i in range(m):
        if hr[i] == sh and mn[i] == sm and i > 1:
            fh, fl, taken, direction, trail = h[i], lo[i], False, 0, np.nan
        dist = (fh - fl) * k
        start = pos
        if not np.isnan(fh) and c[i] > fh and not taken and hr[i] > sh:
            pos, trail, taken, direction = 1, c[i] - dist, True, 1
        if not np.isnan(fl) and c[i] < fl and not taken and hr[i] > sh:
            pos, trail, taken, direction = -1, c[i] + dist, True, -1
        if direction == 1 and not np.isnan(trail):
            trail = max(trail, c[i] - dist)
            if c[i] <= trail and start == 1 and pos == 1:
                pos = 0
        if direction == -1 and not np.isnan(trail):
            trail = min(trail, c[i] + dist)
            if c[i] >= trail and start == -1 and pos == -1:
                pos = 0
        if taken and hr[i] == eh and mn[i] == em:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
