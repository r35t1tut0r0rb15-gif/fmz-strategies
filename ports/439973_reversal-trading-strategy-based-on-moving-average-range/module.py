"""Contrarian SMA 3 / 5 / 8 fans on the SMA 200 side, 1-hour bars: above the SMA 200, a falling fan (3 < 5 < 8) goes long; below it, a rising fan goes short; the opposite fan closes; reversing.
Port of FMZ strategy #439973 "Reversal Trading Strategy Based on Moving Average Range" (Moving Average Trap).

FMZ source id: 439973

Source
    https://www.fmz.com/strategy/439973 (PineScript v5, FMZ last modified 2024-01-25 14:16:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 163-196), SMA 3 / 5 / 8; trend filter SMA 200
    long = fma < sma < ssma and close > tma -> entry long;  closelong = fma > sma > ssma -> close long;  short = fma > sma > ssma and close < tma -> entry short;  closeshort = fma < sma < ssma -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes test the position held at the bar close, after the entries: a short entry on a rising
      fan also closes a held long, and the reversal stands; a long entry on a falling fan reverses a
      short although the short's close follows (as #438020). strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA fans and an SMA side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439973_sma_fan_trap_contrarian"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tlenght": [200, 100],
    "sslenght": [8, 13],
}
DEFAULT_PARAMS = {"tlenght": 200, "sslenght": 8, "flenght": 3, "llenght": 5}


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
    f, s, ss, t = (c.rolling(int(p[k])).mean() for k in ("flenght", "llenght", "sslenght", "tlenght"))
    falling = ((f < s) & (s < ss)).to_numpy()
    rising = ((f > s) & (s > ss)).to_numpy()
    above = (c > t).to_numpy()
    below = (c < t).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if falling[i] and above[i] and pos != 1:
            new = 1
        if pos == 1 and rising[i] and new == 1:
            new = 0
        if rising[i] and below[i] and new != -1:
            new = -1
        if pos == -1 and falling[i] and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
