"""SSL channel cross, 2-hour bars: the close above the SMA 10 of highs flips the channel up and goes long, below the SMA 10
of lows flips it down and goes short; the coded stop exits name a non-existent entry id and never act.
Port of FMZ strategy #430171 "SSL Channel Breakout Strategy with Trailing Stop Loss" (SSL Channel Cross with Trailing Stop and Stop Loss).

FMZ source id: 430171

Source
    https://www.fmz.com/strategy/430171 (PineScript v4, FMZ last modified 2023-10-25 17:40:37).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 183-231), SMA 10 of highs / lows, trailing size 10 points
    Hlv = close > sma(high, 10) ? 1 : close < sma(low, 10) ? -1 : Hlv[1]
    sslUp / sslDown swap with Hlv; crossover(sslUp, sslDown) -> entry long; crossunder -> entry short
    long: trailingStop = max(low - 10, sslDown at the signal); close < it -> strategy.close("ExitLong")  (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * crossover(sslUp, sslDown) happens exactly when Hlv turns from -1 to 1 (the lines swap), and the
      crossunder when it turns to -1 (from 1, or from the start state 0, where sslUp is the upper SMA).
    * The stop exits call strategy.close("ExitLong") / ("ExitShort"), ids no entry uses: they close
      nothing, so the only exits are the reversals (ported as written; the 10-point size, a price
      unit, is therefore inert).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the inert exits stated.
    2 generic: PASS, moving averages of highs and lows.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430171_ssl_channel_flip"
FAMILY = "ssl_channel"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20, 40],
}
DEFAULT_PARAMS = {"length": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    c = bars_df["close"].to_numpy(dtype=float)
    sh = bars_df["high"].rolling(n).mean().to_numpy()
    sl = bars_df["low"].rolling(n).mean().to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    hlv, pos = 0, 0
    for i in range(m):
        prev = hlv
        if c[i] > sh[i]:
            hlv = 1
        elif c[i] < sl[i]:
            hlv = -1
        if prev == -1 and hlv == 1:
            pos = 1
        elif prev != -1 and hlv == -1:                 # from the start state 0 the lines also cross under
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
