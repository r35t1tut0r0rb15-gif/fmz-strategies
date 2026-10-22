"""Dominant-candle breakouts against a 5-bar high / low band, 4-hour bars: a large green candle beating the last three bodies under the band's high line goes long, a large red candle beating the last
three above the low line goes short; the low under the low line closes a long, the high over the high line closes a short; reversing.
Port of FMZ strategy #441013 "Golden Parabola Breakout Strategy" (5MABAND + GBS Buy & Sell Strategy).

FMZ source id: 441013

Source
    https://www.fmz.com/strategy/441013 (PineScript v5, FMZ last modified 2024-02-04 18:07:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 163-199), band: SMA 5 of highs and of lows
    gbsBuy = green, small wicks, body > the three previous bodies, the three previous closes and opens under avgHigh -> entry Buy;  gbsSell = red body > the three previous, opens above avgLow, body > lower and upper wick -> entry Sell
    close < avgLow -> close Buy;  close > avgHigh -> close Sell;  low < avgLow -> close Buy;  high > avgHigh -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close tests are covered by the low / high tests (a close under the low line has its low under
      it), so a long closes on the low under the low line and a short on the high over the high line. A
      close acts only on the held position; a close written after a reversing entry leaves the reversal
      standing (as #438020). strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "4h" from
      the backtest header (bars on UTC multiples of 4 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle pattern and band tests.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: DG441013 (2 members, best partner #441053, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441013_dominant_candle_5ma_band_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [5, 10],
}
DEFAULT_PARAMS = {"length": 5}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ah, al = h.rolling(n).mean(), lo.rolling(n).mean()
    gb = c - o
    rb = o - c
    buy = (c > o) & (h - c < gb) & (o - lo < gb)
    sell = (rb > o - lo) & (rb > h - o)
    for k in (1, 2, 3):
        buy &= (gb > gb.shift(k)) & (c.shift(k) < ah) & (o.shift(k) < ah)
        sell &= (rb > rb.shift(k)) & (o.shift(k) > al)
    buy, sell = buy.to_numpy(), sell.to_numpy()
    xb = (lo < al).to_numpy()
    xs = (h > ah).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if xb[i] and held == 1 and new == 1:
            new = 0
        if xs[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
