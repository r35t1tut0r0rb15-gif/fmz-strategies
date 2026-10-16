"""SSL channel flip: the SMA 13 channel of highs and lows swaps sides when the close breaks out of it;
the up line crossing above the down line goes long, crossing below goes short.
Port of FMZ strategy #427862 "Auto Trading Strategy Based on RB SSL Channel" ("Algo 4- Auto").

FMZ source id: 427862

Source
    https://www.fmz.com/strategy/427862 (PineScript v4, FMZ last modified 2023-09-26 12:04:24).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 97-137), length 13
    Hlv = close > sma(high, 13) ? 1 : close < sma(low, 13) ? -1 : Hlv[1]
    sslDown = Hlv < 0 ? smaHigh : smaLow; sslUp = Hlv < 0 ? smaLow : smaHigh
    crossover(sslUp, sslDown) -> entry long (close short); crossunder -> entry short (close long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The first "Period" input is unused; Hlv starts at 0.
    * The closes coincide with the opposite entries: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
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

NAME = "fmz_427862_ssl_channel_flip"
FAMILY = "ssl_channel"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [13, 20, 30, 50],
}
DEFAULT_PARAMS = {"len": 13}


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
    n = int(p["len"])
    sh = bars_df["high"].rolling(n).mean().to_numpy()
    sl = bars_df["low"].rolling(n).mean().to_numpy()
    c = bars_df["close"].to_numpy(dtype=float)
    m = len(c)
    hlv = np.zeros(m)
    for i in range(m):
        prev = hlv[i - 1] if i else 0.0
        hlv[i] = 1 if c[i] > sh[i] else (-1 if c[i] < sl[i] else prev)
    down = np.where(hlv < 0, sh, sl)
    up = np.where(hlv < 0, sl, sh)
    up1, dn1 = np.concatenate(([np.nan], up[:-1])), np.concatenate(([np.nan], down[:-1]))
    with np.errstate(invalid="ignore"):
        xo = (up > down) & (up1 <= dn1)
        xu = (up < down) & (up1 >= dn1)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if xo[i]:
            pos = 1
        elif xu[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
