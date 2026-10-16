"""Five-bar-low dip with an RSI 2 exit, 1-hour bars, long only from flat: a close under the lowest low of the previous 5
bars goes long; RSI 2 above 50 closes the long, and so does the fifth bar after the entry signal.
Port of FMZ strategy #430556 "Low Point Rebound Strategy" (Hobbiecode - Five Day Low RSI Strategy).

FMZ source id: 430556

Source
    https://www.fmz.com/strategy/430556 (PineScript v5, FMZ last modified 2023-10-30 11:53:56).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 171-197), RSI 2 above 50, 5-bar low, time stop 5 bars
    close < lowest(low[1], 5) and position_size < 1 -> entry long
    long and rsi(close, 2) > 50 -> close;  long and barssince(entry signal) >= 5 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * "position_size < 1" with the default one-unit order means flat: entries only from flat.
    * The time stop is an explicit exit signal on the fifth bar after the entry signal (bars, as
      written; the comment's "days" are the author's daily reading), not max_hold_time.
    * Exits are tested from the bar after the signal (the position exists from the fill).
    * Long only; Opposite entries cannot occur. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the time exit as a signal.
    2 generic: PASS, a price channel and an RSI level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430556_five_bar_low_rsi2_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "low_len": [5, 10],
    "time_stop": [5, 10],
}
DEFAULT_PARAMS = {"low_len": 5, "time_stop": 5, "rsi_len": 2, "rsi_upper": 50}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


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
    lo, c = bars_df["low"], bars_df["close"]
    dip = (c < lo.shift(1).rolling(int(p["low_len"])).min()).to_numpy()
    hot = (_rsi(c, int(p["rsi_len"])) > p["rsi_upper"]).to_numpy()
    ts = int(p["time_stop"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos, sig_i = 0, -1
    for i in range(m):
        if pos == 0 and dip[i]:
            pos, sig_i = 1, i
        elif pos == 1 and i > sig_i and (hot[i] or i - sig_i >= ts):
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
