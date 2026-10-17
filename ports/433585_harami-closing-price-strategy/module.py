"""Noro's harami, 10-minute bars, long only by default: a green candle whose body sits inside the previous red body goes
long; a bearish harami closes the long (shorts are off), and so does a green candle with a body above half the 10-bar
average body.
Port of FMZ strategy #433585 "Harami Closing Price Strategy" (Noro's Harami Strategy v1.0).

FMZ source id: 433585

Source
    https://www.fmz.com/strategy/433585 (PineScript v3, FMZ last modified 2023-11-28 16:50:34).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 134-172), longs on, shorts off; body average 10
    up = green and red[1] and min(o, c) > min[1] and max(o, c) < max[1];  dn = red and green[1] and the same inside test
    up -> close a short, entry long;  dn -> close a long, entry short (qty 0: shorts off)
    exit = (long and green or short and red) and body > sma(body, 10) / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * needshort is false, so the short entry carries quantity 0 and places nothing: a bearish harami
      only closes the long. The exit tests the position held at the start of the bar; an entry from
      flat on that bar stands.
    * Long only; Opposite entries cannot occur. The date window is open. FREQ = "10min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle shapes and body ratios.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
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

NAME = "fmz_433585_noro_harami_long"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "body_len": [10, 20],
    "exit_frac": [0.5, 1.0],
}
DEFAULT_PARAMS = {"body_len": 10, "exit_frac": 0.5}


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
    body = (c - o).abs()
    big = (body > body.rolling(int(p["body_len"])).mean() * float(p["exit_frac"])).to_numpy()
    mn = pd.concat([c, o], axis=1).min(axis=1)
    mx = pd.concat([c, o], axis=1).max(axis=1)
    green, red = c > o, c < o
    inside = (mn > mn.shift(1)) & (mx < mx.shift(1))
    up = (green & red.shift(1, fill_value=False) & inside).to_numpy()
    dn = (red & green.shift(1, fill_value=False) & inside).to_numpy()
    gv = green.to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 1:
            if dn[i] or (gv[i] and big[i]):
                pos = 0
        elif up[i]:
            pos = 1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
