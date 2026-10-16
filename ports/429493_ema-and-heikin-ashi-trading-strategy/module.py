"""Heikin Ashi close vs EMA 15 / EMA 50, hourly bars: the HA close above both EMAs with EMA 15 above EMA 50 goes long,
the mirror goes short; the HA close crossing back through EMA 15 closes the position.
Port of FMZ strategy #429493 "EMA and Heikin Ashi Trading Strategy" (EMA & Heikin Ashi).

FMZ source id: 429493

Source
    https://www.fmz.com/strategy/429493 (PineScript v3, FMZ last modified 2023-10-17 16:11:19).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 152-178), EMA 15 / 50, HA close
    haclose = security(heikinashi, same period, close) = ohlc4 of the bar
    long = haclose > ema15 and haclose > ema50 and ema15 > ema50 -> entry long; short = mirror -> entry short
    haclose < ema15 -> close long; haclose > ema15 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Heikin Ashi close on the chart's own period is (open + high + low + close) / 4 of the bar.
    * An entry on the opposite side reverses in one bar: REVERSAL INTENDED. The 2018 start is dropped.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average comparisons only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() capital stored.
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

NAME = "fmz_429493_ha_close_ema15_50"
FAMILY = "heikin_ashi_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [15, 10],
    "ma2": [50, 100],
}
DEFAULT_PARAMS = {"ma1": 15, "ma2": 50}


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
    ha = (o + h + lo + c) / 4
    m1 = c.ewm(span=int(p["ma1"]), adjust=False).mean()
    m2 = c.ewm(span=int(p["ma2"]), adjust=False).mean()
    lc = ((ha > m1) & (ha > m2) & (m1 > m2)).to_numpy()
    sc = ((ha < m1) & (ha < m2) & (m1 < m2)).to_numpy()
    cl, cs = (ha < m1).to_numpy(), (ha > m1).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if lc[i]:
            pos = 1
        elif sc[i]:
            pos = -1
        elif pos == 1 and cl[i]:
            pos = 0
        elif pos == -1 and cs[i]:
            pos = 0
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
