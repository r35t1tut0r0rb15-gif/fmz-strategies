"""Buys at the end of a downtrend held to the end of the data, 1-hour bars, long only: the first bar with the EMA 50 under the EMA 200 and the EMA-difference histogram negative but rising against 2 bars
ago buys; later monthly buys only add (sizing); the only close is on the last bar.
Port of FMZ strategy #439111 "Dollar Cost Averaging After Downtrend Strategy" (DCA After Downtrend v2).

FMZ source id: 439111

Source
    https://www.fmz.com/strategy/439111 (PineScript v5, FMZ last modified 2024-01-17 17:57:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 154-224), EMA 50 / 200, signal 20; one entry per 720 bars; pyramiding 1000; cash 1000 per entry, commission 1.1 %; dates 2017-2050
    nPastCandles > entryNumber x 720 and emacd < 0 and hist < 0 and hist > hist[2] -> entry 'Long n';  barstate.islast or the last two hours -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every later entry is an add to the same long (pyramiding 1000, fixed cash each): sizing, so the port
      holds one position from the first entry; the close_all fires only on the last bar of the data (or
      the last two hours before timenow), so the position is held to the end, as written; the port sends
      no last-bar signal (it would depend on where the data ends and never fill). The 2017-2050
      window covers the data. Long only. The cash size and commission are sizing / costs. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA difference histogram turn.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash size, pyramiding and commission stored.
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

NAME = "fmz_439111_downtrend_end_buy_and_hold"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 20],
    "slow": [200, 100],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200, "signal": 20}


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
    emacd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = emacd - emacd.ewm(span=int(p["signal"]), adjust=False).mean()
    cond = ((emacd < 0) & (hist < 0) & (hist > hist.shift(2))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    hits = np.flatnonzero(cond[:-1]) if m > 1 else np.array([], dtype=int)
    if len(hits):
        le[hits[0]] = True                               # later buys only add (sizing)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
