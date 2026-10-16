"""Alorse EMA + RSI, long only, 2-hour bars: EMA 10 crossing above EMA 20 while above EMA 100 on a green
bar goes long; close when RSI 14 is above 70, or after 24 bars in the trade when the close is above the
entry price.
Port of FMZ strategy #427881 "Trend Following EMA and RSI Strategy" (Tendency EMA + RSI [Alorse]).

FMZ source id: 427881

Source
    https://www.fmz.com/strategy/427881 (PineScript v5, FMZ last modified 2023-09-26 15:39:48).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 131-187), RSI 14, EMAs 10 / 20 / 100, 24 bars
    entryLong = crossover(ema10, ema20) and ema10 > ema100 and close > open -> entry long
    exitLong = rsi > 70, or (nPastBars >= 24 and close > entry price) -> close
    entry price = open of the fill bar; nPastBars counts the bars with an open position (from the fill bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line is commented out: Pine defaults (one position).
    * Short entries are off by default: Long only.
    * An entry and an exit on one bar: the close acts only on an open position.
    * FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the bar count and entry price are known at the close.
    2 generic: PASS, MA lengths, RSI level, bar count.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() sizing stored in original_sizing.txt.
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

NAME = "fmz_427881_alorse_ema_rsi_long"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "x_bars": [24, 12],
    "len_c": [100, 200],
}
DEFAULT_PARAMS = {"len": 14, "len_a": 10, "len_b": 20, "len_c": 100, "x_bars": 24, "rsi_exit": 70}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


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
    o, c = bars_df["open"], bars_df["close"]
    d = c.diff()
    n = int(p["len"])
    up, dn = _rma(d.clip(lower=0), n), _rma(-d.clip(upper=0), n)
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).to_numpy()
    a = c.ewm(span=int(p["len_a"]), adjust=False).mean()
    b = c.ewm(span=int(p["len_b"]), adjust=False).mean()
    e_c = c.ewm(span=int(p["len_c"]), adjust=False).mean()
    entry = ((a > b) & (a.shift(1) <= b.shift(1)) & (a > e_c) & (c > o)).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, held_n, entry_px = 0, 0, np.nan
    xb = int(p["x_bars"])
    for i in range(m):
        held = i > 0 and tgt[i - 1] == 1            # position open during bar i (filled at an open)
        if held:
            if held_n == 0:
                entry_px = ov[i]
            held_n += 1
        else:
            held_n = 0
        start = pos
        exit_l = (rsi[i] > p["rsi_exit"]) or (held_n >= xb and cv[i] > entry_px)
        if start == 1 and exit_l:
            pos = 0
        if start == 0 and entry[i]:
            pos = 1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
