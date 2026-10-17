"""First-candle breakout with a close-checked range stop and an end-of-day close, 1-minute bars: the 09:15 candle's
high and low are recorded; from 10:00 the first close above the high goes long (below the low goes short), one trade a
day; a close back through the opposite side closes it, and everything closes at 15:30.
Port of FMZ strategy #489035 "首个蜡烛突破-止损或收盘自动平仓策略-First-Candle-Breakout-with-Stop-Loss-or-End-of-Day-Closing-Strategy" (First Candle Breakout - Close on SL or EOD).

FMZ source id: 489035

Source
    https://www.fmz.com/strategy/489035 (PineScript v5, FMZ last modified 2025-04-01 13:51:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 121-163), first candle 09:15, end 15:30 (exchange time)
    the 09:15 bar sets firstHigh / firstLow and resets tradeTaken and the direction
    long = close > firstHigh and not tradeTaken and hour > 9 -> entry long (short mirrored with firstLow)
    long: close <= firstLow -> close;  short: close >= firstHigh -> close;  tradeTaken and 15:30 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Session open (check 9 / C6): 09:15 and 15:30 are clock times in the chart's time zone. As written on the
      author's Binance chart that is UTC (session_tz "UTC", the default); the inputs say "exchange time" and the
      times are the NSE session (09:15-15:30 Asia/Kolkata, no DST), the grid's second reading. "hour > 9" means from
      10:00 local.
    * The stop is checked on closes: a close-based exit (rule 3). The close_all at 15:30 is written last and leaves the
      bar flat (desktop convention). One trade a day; the first range persists if a day has no 09:15 bar.
    * Entries reverse only if a trade survived to another day (REVERSAL INTENDED). FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and close-checked exits.
    2 generic: PASS, the first candle's range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 09:15 first candle and 15:30 close in session_tz (UTC as written; Asia/Kolkata, no DST, as the variant).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489035_first_candle_breakout_eod"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "session_tz": ["UTC", "Asia/Kolkata"],
}
DEFAULT_PARAMS = {"session_tz": "UTC", "start_hour": 9, "start_minute": 15, "end_hour": 15, "end_minute": 30}


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
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos, fh, fl, taken, direction = 0, np.nan, np.nan, False, 0
    for i in range(m):
        if hr[i] == sh and mn[i] == sm and i > 1:
            fh, fl, taken, direction = h[i], lo[i], False, 0
        start = pos
        if not np.isnan(fh) and c[i] > fh and not taken and hr[i] > sh:
            pos, taken, direction = 1, True, 1
        if not np.isnan(fl) and c[i] < fl and not taken and hr[i] > sh:
            pos, taken, direction = -1, True, -1
        if direction == 1 and c[i] <= fl and start == 1 and pos == 1:
            pos = 0
        if direction == -1 and c[i] >= fh and start == -1 and pos == -1:
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
