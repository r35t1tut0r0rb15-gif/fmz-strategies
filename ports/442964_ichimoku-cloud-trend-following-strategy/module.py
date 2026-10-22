"""Ichimoku TK crosses above / below the cloud, 1-hour bars: the conversion line crossing over the base line with the close above it and above a green cloud goes long, the mirror short; the close falling
back through the conversion line closes; reversing.
Port of FMZ strategy #442964 "Ichimoku Cloud Trend Following Strategy" (Ichimoku Cloud - BitBell).

FMZ source id: 442964

Source
    https://www.fmz.com/strategy/442964 (PineScript v5, FMZ last modified 2024-02-27 16:41:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 124-194), conversion 9, base 26, span B 52, displacement 26; trail line ConversionLine
    leadA = avg(conv, base)[25];  leadB = donchian(52)[25];  long = close > leadA, leadB and crossover(conv, base) and close > conv and leadA > leadB -> entry Long
    close < conv and long -> close Long;  short mirrored -> entry Short;  close > conv and short -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cloud is the spans 25 bars back (displacement - 1), the value plotted at the current bar.
      ta.lowest / ta.highest with one argument use the low / high. Ported in call order with one
      position at a time; each close acts only on a held position. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, TK crosses with the cloud.
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

NAME = "fmz_442964_ichimoku_tk_cross_cloud_conv_exit"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion": [9, 20],
    "span_b": [52, 120],
}
DEFAULT_PARAMS = {"conversion": 9, "span_b": 52, "base": 26, "displacement": 26}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def don(n):
        return (lo.rolling(n).min() + h.rolling(n).max()) / 2

    conv, base = don(int(p["conversion"])), don(int(p["base"]))
    k = int(p["displacement"]) - 1
    la = ((conv + base) / 2).shift(k)
    lb = don(int(p["span_b"])).shift(k)
    up_x = (conv > base) & (conv.shift(1) <= base.shift(1))
    dn_x = (conv < base) & (conv.shift(1) >= base.shift(1))
    lg = ((c > la) & (c > lb) & up_x & (c > conv) & (la > lb)).to_numpy()
    sh = ((c < la) & (c < lb) & dn_x & (c < conv) & (la < lb)).to_numpy()
    xl = (c < conv).to_numpy()
    xs = (c > conv).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if lg[i] and new != 1:
            new = 1
        if xl[i] and held == 1 and new == 1:
            new = 0
        if sh[i] and new != -1:
            new = -1
        if xs[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
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
