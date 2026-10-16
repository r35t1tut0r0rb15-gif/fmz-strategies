"""TRIX simple, hourly bars: in an up trend (SMA 13 above SMA 68, TRIX band above zero, TRIX 7 under its
band) the fast TRIX 4 crossing above TRIX 7 goes long; the mirror goes short.
Port of FMZ strategy #428683 "Trix Simple Trend Following Strategy".

FMZ source id: 428683

Source
    https://www.fmz.com/strategy/428683 (PineScript v3, FMZ last modified 2023-10-08 12:17:21).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 177-204), TRIX 7 / 4 of log(close), band SMA 20, SMA 13 / 68
    trix = 10000 change(ema(ema(ema(log(close), 7), 7), 7)); trix1 likewise with 4; band = sma(trix, 20)
    long trend = sma13 > sma68 and band > 0 and trix < band -> entry long on crossover(trix1, trix)
    short trend mirrors -> entry short on crossunder(trix1, trix)
    strategy.exit("Buy" / "Sell", when = cross(trix, band)) carries no price: no exit order

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits have no stop / limit / trail, so they place nothing (as written): positions change
      only on the opposite entry. The "ema13" is an SMA as written.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, log-price oscillators and MA lengths.
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

NAME = "fmz_428683_trix_simple"
FAMILY = "trix"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lengtha": [7, 14],
    "lengtha1": [4, 2],
}
DEFAULT_PARAMS = {"lengtha": 7, "lengtha1": 4, "bb": 20, "fast_sma": 13, "slow_sma": 68}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _trix(lc, n):
    e = lc.ewm(span=n, adjust=False).mean().ewm(span=n, adjust=False).mean().ewm(span=n, adjust=False).mean()
    return 10000 * e.diff()


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
    c = bars_df["close"]
    lc = np.log(c)
    t, t1 = _trix(lc, int(p["lengtha"])), _trix(lc, int(p["lengtha1"]))
    band = t.rolling(int(p["bb"])).mean()
    f, s = c.rolling(int(p["fast_sma"])).mean(), c.rolling(int(p["slow_sma"])).mean()
    long_c = (f > s) & (band > 0) & (t < band)
    short_c = (f < s) & (band < 0) & (t > band)
    up = (long_c & (t1 > t) & (t1.shift(1) <= t.shift(1))).to_numpy()
    dn = (short_c & (t1 < t) & (t1.shift(1) >= t.shift(1))).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
