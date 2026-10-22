"""Marubozu candles with their directions inverted as written, 1-hour bars: a black marubozu (long body, shadows within 5 %) buys, a white marubozu sells; after two down bars an up bar closes the sell, after
two up bars a down bar closes the buy; reversing.
Port of FMZ strategy #442641 "Marubozu Candle Range Balance Strategy" (Marubozu).

FMZ source id: 442641

Source
    https://www.fmz.com/strategy/442641 (PineScript v4, FMZ last modified 2024-02-23 14:23:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 155-211), body EMA 14; shadows <= 5 % of the body; 100 % of equity, capital 1000, commission 0
    black marubozu -> strategy.entry("short", 1) (direction 1 = long);  white marubozu -> strategy.entry("long", 0) (direction 0 = short)
    close[1] < open[1] and close[2] < open[2] and close > open -> close "long";  close[1] > open[1] and close[2] > open[2] and close < open -> close "short"

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry's second argument is the direction: the id "short" is entered long and "long"
      short, as written (as #442377); each close names its id, so "long" closes the short position.
      Ported in call order with one position at a time. strategy.entry reverses: REVERSAL INTENDED. The
      100 % of equity size, capital and commission are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, marubozu candle pattern (directions as written).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
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

NAME = "fmz_442641_marubozu_inverted_direction_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "body_len": [14, 30],
    "shadow_pct": [5.0, 10.0],
}
DEFAULT_PARAMS = {"body_len": 14, "shadow_pct": 5.0}


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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    bh, bl = np.maximum(o, c), np.minimum(o, c)
    body = bh - bl
    longb = body > body.ewm(span=int(p["body_len"]), adjust=False).mean()
    sp = float(p["shadow_pct"]) / 100
    clean = ((h - bh) <= sp * body) & ((bl - lo) <= sp * body)
    white = ((o < c) & longb & clean).to_numpy()
    black = ((o > c) & longb & clean).to_numpy()
    up, dn = c > o, c < o
    x_l = (dn.shift(1, fill_value=False) & dn.shift(2, fill_value=False) & up).to_numpy()   # closes "long" (short side)
    x_s = (up.shift(1, fill_value=False) & up.shift(2, fill_value=False) & dn).to_numpy()   # closes "short" (long side)
    side = {None: 0, "short": 1, "long": -1}
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = None
    for i in range(m):
        new = held
        if black[i] and side[new] != 1:
            new = "short"
        if white[i] and side[new] != -1:
            new = "long"
        if x_l[i] and held == "long" and new == "long":
            new = None
        if x_s[i] and held == "short" and new == "short":
            new = None
        tgt[i] = side[new]
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
