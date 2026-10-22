"""A latched SMA 9 / 20 cross-up followed by a green bar closing above the SMA 9, 1-hour bars, long only: that bar goes long (and clears the latch); any close under the SMA 9 closes.
Port of FMZ strategy #446444 "Moving Average Crossover Quantitative Strategy" (Simple 9/20 Crossover).

FMZ source id: 446444

Source
    https://www.fmz.com/strategy/446444 (PineScript v5, FMZ last modified 2024-03-28 16:55:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 150-187), SMA 9 / 20
    crossover(ma9, ma20) -> latch on;  crossunder -> latch off;  latch and close > open and close > ma9 -> entry Long, latch off;  close < ma9 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The latch is set by the cross-up, cleared by a cross-down or by the entry; the entry and the
      close cannot meet on one bar. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, latched SMA cross with a confirming bar, SMA 9 exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_446444_sma9_20_latched_cross_green_confirm_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 20}


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
    o, c = bars_df["open"], bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    xo = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    xu = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    conf = ((c > o) & (c > f)).to_numpy()
    out = (c < f).to_numpy()
    m = len(xo)
    le = np.zeros(m, dtype=bool)
    latch = False
    for i in range(m):
        if xo[i]:
            latch = True
        if xu[i]:
            latch = False
        if latch and conf[i]:
            le[i] = True
            latch = False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(out, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
