"""Monday crossings of an ALMA 17, 1-hour bars, long only: on a Monday (UTC) bar, a close crossing above the ALMA buys; a Sunday bar closes; each trade has a 10 % stop and a 30 % target from the fill.
Port of FMZ strategy #438465 "Multi Timeframe Moving Average Combined with Trading Hours Quantitative Trading Strategy" (Time MA strategy).

FMZ source id: 438465

Source
    https://www.fmz.com/strategy/438465 (PineScript v5, FMZ last modified 2024-01-12 11:50:37).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 116-278), long entries on, short entries off; source close; length 17, type ALMA (offset 0.85, sigma 6); long SL 10 %, TP 30 % (short 5 % / 10 % unused)
    long = close > ma and close[1] < ma and dayofweek == monday -> entry long;  exit(limit = avg x 1.3, stop = avg x 0.9);  dayofweek == sunday -> close long;  short side off

Interpretation choices (Pine rules in SURVEY_README.md)
    * dayofweek is read on the bar's UTC open time (the exchange time zone, as #435514). The cross test
      compares close[1] with the current ALMA, as written. The ALMA weights follow Pine (offset 0.85 x
      (n - 1), sigma n / 6); the MA type is swept over ALMA and EMA (the other types are not swept). The
      bracket is sent from the first bar close inside the trade; the port fixes it at the fill. Long only
      (short entries off). Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, ALMA crossings on Mondays; Sunday close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: UTC weekday of the bar (Monday entries, Sunday close).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438465_monday_alma_cross_long"
FAMILY = "calendar_seasonal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "len": [17, 34],
    "ma_type": ["ALMA", "EMA"],
}
DEFAULT_PARAMS = {"len": 17, "ma_type": "ALMA", "stop": 0.10, "take": 0.30}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _alma(x, n, offset=0.85, sigma=6.0):
    m = offset * (n - 1)
    s = n / sigma
    w = np.exp(-((np.arange(n) - m) ** 2) / (2 * s * s))   # oldest .. newest
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["len"])
    ma = _alma(c, n) if p["ma_type"] == "ALMA" else c.ewm(span=n, adjust=False).mean()
    dow = bars_df.index.tz_convert("UTC").dayofweek
    le = (c > ma) & (c.shift(1) < ma) & (dow == 0)
    lx = pd.Series(dow == 6, index=c.index)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop"]), "tp_stop": float(p["take"])}


def portfolio_kwargs(**params):
    return {}
