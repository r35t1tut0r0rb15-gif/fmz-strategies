"""Ichimoku cloud side with SMA and ohlc4 momentum, 2-hour bars: ohlc4 rising, lead line 1 above lead line 2 and
the SMA 19 above the SMA 21 (of the previous ohlc4) goes long, the mirror goes short; ohlc4 below both its
value 21 bars ago and the previous bar closes a long (mirror for shorts).
Port of FMZ strategy #429382 "均线Ichimoku交叉策略SMA-Ichimoku-Crossover-Strategy" (Ichimoku+SMAsmoothed).

FMZ source id: 429382

Source
    https://www.fmz.com/strategy/429382 (PineScript v3, FMZ last modified 2023-10-16 15:46:38).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 184-233), Ichimoku 9 / 26 / 52, SMA 21 / 19 of ohlc4[1]
    closelong = ohlc4 < ohlc4[21] and ohlc4 < ohlc4[1]; closeshort = ohlc4 > ohlc4[21] and ohlc4 > ohlc4[1]
    long = ohlc4 > ohlc4[1] and lead1 > lead2 and sma(ohlc4[1],19)/24 > sma(ohlc4[1],21)/24 -> entry long
    short = ohlc4 < ohlc4[1] and lead1 < lead2 and sma19 < sma21 (same scaling) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * p_h > p_d is (2 x sma19 - sma19) / 24 > (2 x sma21 - sma21) / 24, i.e. sma19 > sma21.
      Lead lines are read at the current bar (not displaced): no look-ahead.
    * The strategy() line (calc_on_every_tick, calc_on_order_fills) is commented out: bar-close orders.
    * Closes come before entries in the source; an entry reverses: REVERSAL INTENDED.
      FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders (the intrabar settings are in a commented-out line).
    2 generic: PASS, comparisons of averages and lines from the bars only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() stored.
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

NAME = "fmz_429382_ichimoku_sma_ohlc4"
FAMILY = "ichimoku"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_long": [21, 30],
    "sma_short": [19, 10],
}
DEFAULT_PARAMS = {"conv": 9, "base": 26, "span2": 52, "sma_long": 21, "sma_short": 19}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    don = lambda n: (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2  # noqa: E731
    lead1 = (don(p["conv"]) + don(p["base"])) / 2
    lead2 = don(p["span2"])
    x = (o + h + lo + c) / 4
    pr = x.shift(1)
    n1 = int(p["sma_long"])
    ma1, ma2 = pr.rolling(n1).mean(), pr.rolling(int(p["sma_short"])).mean()
    close_long = ((x < x.shift(n1)) & (x < x.shift(1))).to_numpy()
    close_short = ((x > x.shift(n1)) & (x > x.shift(1))).to_numpy()
    long_c = ((x > x.shift(1)) & (lead1 > lead2) & (ma2 > ma1)).to_numpy()
    short_c = ((x < x.shift(1)) & (lead1 < lead2) & (ma2 < ma1)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 1 and close_long[i]:
            pos = 0
        if pos == -1 and close_short[i]:
            pos = 0
        if long_c[i]:
            pos = 1
        if short_c[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
