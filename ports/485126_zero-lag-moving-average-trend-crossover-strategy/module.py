"""Zero-lag EMA 15 crossings of the EMA 15, hourly bars, long only: the up-cross goes long, the down-cross closes; a bar at 15:45 UTC or later in hour 15 would close everything (it never comes on hourly bars).
Port of FMZ strategy #485126 "Zero Lag Moving Average Trend Crossover Strategy" (Zero-Lag MA Trend Strategy).

FMZ source id: 485126

Source
    https://www.fmz.com/strategy/485126 (PineScript v5, FMZ last modified 2025-03-06 11:06:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 137-184), length 15; EOD close at hour 15, minute >= 45; 10 % of equity; MPL 2.0 notice (ChartPrime)
    ema = ema(close, 15);  zlma = ema(close + (close - ema), 15);  crossover(zlma, ema) -> entry Long;  crossunder -> close Long
    hour == 15 and minute >= 45 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour / minute read the chart exchange's zone, UTC for the header's Binance pair. On hourly bars the
      bar's minute is always 0, so the end-of-day close never fires, as written; it is kept for other
      bar sizes. Long only. The 10 % of equity size is sizing. The MPL 2.0 notice is kept with the
      verbatim copy (ported, stated). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, zero-lag EMA crossings.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: end-of-day close at 15:45 UTC (fixed UTC, no DST; the header exchange's time zone; never reached on hourly bars).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_485126_zlema15_ema15_cross_long"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
SESSION_TZ = "UTC"  # hour / minute read the chart exchange's zone: UTC for the header's Binance pair

GRID = {
    "length": [15, 30, 50],
}
DEFAULT_PARAMS = {"length": 15, "close_hour": 15, "close_minute": 45}


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
    n = int(p["length"])
    e = c.ewm(span=n, adjust=False).mean()
    z = (c + (c - e)).ewm(span=n, adjust=False).mean()
    le = (z > e) & (z.shift(1) <= e.shift(1))
    loc = bars_df.index.tz_convert(SESSION_TZ)
    eod = pd.Series((np.asarray(loc.hour) == int(p["close_hour"])) &
                    (np.asarray(loc.minute) >= int(p["close_minute"])), index=c.index)
    lx = ((z < e) & (z.shift(1) >= e.shift(1))) | eod
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}
