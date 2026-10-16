"""Connors-style RSI 2, 1-hour bars: RSI 2 crossing up through 10 after a bar above the SMA 200, below the SMA 5 with RSI
under 10 goes long; RSI crossing down through 90 after the mirror bar goes short; the opposite RSI cross without its
setup closes the position.
Port of FMZ strategy #430271 "RSI多空动量策略RSI-Momentum-Long-Short-Strategy" (SB_CM_RSI_2_Strategy_Version 2.0).

FMZ source id: 430271

Source
    https://www.fmz.com/strategy/430271 (PineScript v3, FMZ last modified 2023-10-26 17:05:40).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 152-191), RSI 2 (Wilder), SMA 5 / 200, levels 10 / 90
    chk = close > sma200 and close < sma5 and rsi < 10 ? 1 : close < sma200 and close > sma5 and rsi > 90 ? -1 : 0
    crossover(rsi, 10) and chk[1] == 1 -> entry long, entry := 1
    crossunder(rsi, 90) and chk[1] == -1 -> entry short, entry := -1
    crossover(rsi, 10) and entry == -1 -> close_all, entry := 0;  crossunder(rsi, 90) and entry == 1 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * "entry" is the script's own position state, updated by the entry block before the close block
      is tested: a short meeting a qualified up-cross reverses to long (the close test then sees
      entry == 1); an unqualified up-cross closes it. Mirrored for longs.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and moving averages.
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

NAME = "fmz_430271_connors_rsi2_long_short"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "over_sold": [10, 5],
    "ma_long": [200, 100],
}
DEFAULT_PARAMS = {"over_sold": 10, "ma_long": 200, "ma_short": 5, "rsi_len": 2}


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
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    lo_l, hi_l = float(p["over_sold"]), 100 - float(p["over_sold"])
    ma5, ma200 = c.rolling(int(p["ma_short"])).mean(), c.rolling(int(p["ma_long"])).mean()
    chk = np.where((c > ma200) & (c < ma5) & (r < lo_l), 1, np.where((c < ma200) & (c > ma5) & (r > hi_l), -1, 0))
    chk1 = np.concatenate(([0], chk[:-1]))
    xo = ((r > lo_l) & (r.shift(1) <= lo_l)).to_numpy()
    xu = ((r < hi_l) & (r.shift(1) >= hi_l)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if xo[i] and chk1[i] == 1:
            pos = 1
        if xu[i] and chk1[i] == -1:
            pos = -1
        if xo[i] and pos == -1:
            pos = 0
        if xu[i] and pos == 1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
