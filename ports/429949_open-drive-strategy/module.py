"""Open drive at the London / New York opens, 10-minute bars: in the first 15 minutes after 07:00, 08:00, 13:00 or 14:30
London time, a bar that opens near its low, closes near its high and breaks above the previous 5-bar range by a full
range goes long (mirror short); the source's limit exit is described, not emitted.
Port of FMZ strategy #429949 "Open Drive Strategy" (Open Drive).

FMZ source id: 429949

Source
    https://www.fmz.com/strategy/429949 (PineScript v5, FMZ last modified 2023-10-23 15:13:49).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 158-303), windows 07:00 / 08:00 / 13:00 / 14:30-+15 min (GB), thresholds 0.15, range 5 bars
    OD_Up = green, (open - low) / range < 0.15, (high - close) / range < 0.15, high >= highest(5)[1] + range5[1], in a window -> entry long (2)
    OD_Down = the mirror -> entry short (2)
    barssince(signal) > 3 -> exit(limit = close) re-placed every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The session strings are London time (time(..., "GB")): Europe/London with its daylight saving.
      A 10-minute bar is in a window when its open time is inside it (07:00 and 07:10, ...).
    * highest(5) / lowest(5) include the current bar; the extension compares with the previous bar's.
    * The exit is a limit order at the current close, placed from the fourth bar after the signal and
      re-placed every bar: a moving level that stops() cannot express (rule 2). Not emitted; mark
      trailing_stop_pending, described in PORT_NOTES. Positions otherwise change only by the opposite
      entry (strategy.entry reverses: REVERSAL INTENDED). FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close entries; the moving limit exit is not emitted (rule 2).
    2 generic: PASS, range ratios only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 2-contract quantity and the commission stored; the exit quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entry windows 07:00-07:15, 08:00-08:15, 13:00-13:15 and 14:30-14:45 Europe/London (DST by the zone).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_429949_london_ny_open_drive"
FAMILY = "momentum_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "threshold": [0.15, 0.25],
    "range_len": [5, 10],
}
DEFAULT_PARAMS = {"threshold": 0.15, "range_len": 5}
_WINDOWS = [(420, 435), (480, 495), (780, 795), (870, 885)]   # minutes after London midnight


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    lon = bars_df.index.tz_convert("Europe/London")
    mins = np.asarray(lon.hour * 60 + lon.minute)
    win = np.zeros(len(c), dtype=bool)
    for a, b in _WINDOWS:
        win |= (mins >= a) & (mins < b)
    n = int(p["range_len"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    rng = hh - ll
    br = (h - lo).replace(0.0, np.nan)
    t = float(p["threshold"])
    up = (c > o) & ((o - lo) / br < t) & ((h - c) / br < t) & (h >= hh.shift(1) + rng.shift(1))
    dn = (c < o) & ((h - o) / br < t) & ((c - lo) / br < t) & (lo <= ll.shift(1) - rng.shift(1))
    idx = bars_df.index
    long_e = pd.Series(up.to_numpy() & win, index=idx)
    short_e = pd.Series(dn.to_numpy() & win & ~long_e.to_numpy(), index=idx)
    false = pd.Series(False, index=idx)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
