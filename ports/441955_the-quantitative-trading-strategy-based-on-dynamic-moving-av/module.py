"""Monday-to-Wednesday dip hold, 2-hour bars, long only: the Monday bar opening in 10:00-11:01 UTC with the close under the HMA 115 goes long; the Wednesday bar opening in that window closes.
Port of FMZ strategy #441955 "The Quantitative Trading Strategy Based on Dynamic Moving Average Breakthrough Entry" (Strategia HMA + LUN/MER).

FMZ source id: 441955

Source
    https://www.fmz.com/strategy/441955 (PineScript v5, FMZ last modified 2024-02-18 09:53:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 198-230), HMA 115; Monday / Wednesday session 1000-1101; stop 0.8 %, target 1.5 % (placed on a non-existent entry id)
    isLong = dayofweek == monday and time in 1000-1101 and close < hma115 -> entry Enter Long;  position open and isExit (wednesday, 1000-1101) -> close Enter Long, strategy.exit("Exit", "Exit", stop, limit)

Interpretation choices (Pine rules in SURVEY_README.md)
    * dayofweek and the session are read on the UTC bar open: on 2-hour bars the 10:00 bar. The
      strategy.exit names from_entry "Exit", which no entry has, so it never acts; the stop and target
      are not ported. Long only. No sizing code. FREQ = "2h" from the backtest header (bars on UTC multiples
      of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, weekday window and HMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entries on the Monday bar opening 10:00-11:01 UTC, exits on the Wednesday one (bar open time).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441955_monday_dip_under_hma115_wednesday_exit_long"
FAMILY = "calendar_seasonal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hma_len": [115, 55],
}
DEFAULT_PARAMS = {"hma_len": 115}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(src, n):
    return _wma(2 * _wma(src, n // 2) - _wma(src, n), int(round(np.sqrt(n))))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    t = bars_df.index.tz_convert("UTC")
    mins = t.hour * 60 + t.minute
    win = (mins >= 600) & (mins < 661)
    mon = pd.Series((t.dayofweek == 0) & win, index=c.index)
    wed = pd.Series((t.dayofweek == 2) & win, index=c.index)
    le = mon & (c < _hma(c, int(p["hma_len"])))
    false = pd.Series(False, index=c.index)
    return le, wed, false, false.copy()


def portfolio_kwargs(**params):
    return {}
