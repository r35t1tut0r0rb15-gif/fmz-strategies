"""LUBE (price friction): friction = how many of the last 500 bars' ranges contain the current close,
weighted towards recent bars. When friction is below a low threshold of its recent range, a rising
FIR filter goes long and a falling one goes short; friction rising above the middle of its range
closes the position.
Port of FMZ strategy #427391 "Trend Following Strategy Based on Price Friction Zones".

FMZ source id: 427391

Source
    https://www.fmz.com/strategy/427391 (PineScript v4, FMZ last modified 2023-09-20 16:46:17).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 164-228), bars back 500, friction level 50, trigger -10, range 100
    friction = sum_{i=1..500} [high[i] >= close >= low[i]] x (1 + 500) / (i + 500)
    lowf / highf = lowest / highest(friction, 100); midf = lowf (1 - 0.5) + highf 0.5; lowf2 = lowf (1 + 0.1) - 0.1 highf
    fir = (4 c + 3 c[1] + 2 c[2] + c[3]) / 10; trend = fir > fir[1] ? 1 : -1
    long = friction < lowf2[5] and trend 1; short = friction < lowf2[5] and trend -1; end = friction > midf[5]
    long -> entry long; short or end -> close long; short -> entry short; long or end -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The friction count uses the 500 bars BEFORE the current one (i = 1..500) against the current
      close; the thresholds are read 5 bars back ([5]), as written. nz() in the FIR filter as written.
    * The leverage-based quantity is sizing. barcount > 20 only skips the first 20 bars.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, counts of bars and a linear filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: leverage / contracts stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427391_lube_price_friction"
FAMILY = "momentum_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "barsback": [500, 200],
    "range": [100, 50],
    "tlevel": [-10, 0],
}
DEFAULT_PARAMS = {"barsback": 500, "flevel": 50, "tlevel": -10, "range": 100}


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
    nb = int(p["barsback"])
    h = bars_df["high"].to_numpy(dtype=float)
    lo = bars_df["low"].to_numpy(dtype=float)
    c = bars_df["close"].to_numpy(dtype=float)
    m = len(c)
    fr = np.zeros(m)
    for i in range(1, nb + 1):
        if i >= m:
            break
        hi_i = np.concatenate((np.full(i, np.nan), h[:-i]))
        lo_i = np.concatenate((np.full(i, np.nan), lo[:-i]))
        fr += np.where((hi_i >= c) & (lo_i <= c), (1 + nb) / (i + nb), 0.0)
    fr = pd.Series(fr, index=bars_df.index)
    k = int(p["range"])
    lowf, highf = fr.rolling(k).min(), fr.rolling(k).max()
    fl, tl = p["flevel"] / 100, p["tlevel"] / 100
    midf = lowf * (1 - fl) + highf * fl
    lowf2 = lowf * (1 - tl) + highf * tl
    cs = bars_df["close"]
    fir = (4 * cs + 3 * cs.shift(1).fillna(0.0) + 2 * cs.shift(2).fillna(0.0) + cs.shift(3).fillna(0.0)) / 10
    trend = np.where(fir > fir.shift(1), 1, -1)
    low_zone = (fr < lowf2.shift(5)).to_numpy()
    end = (fr > midf.shift(5)).to_numpy()
    long_c, short_c = low_zone & (trend == 1), low_zone & (trend == -1)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if i <= 20:
            tgt[i] = 0
            continue
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        elif end[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
