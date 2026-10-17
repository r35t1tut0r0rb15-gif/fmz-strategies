"""Triple EMA alignment (Jompatan), 1-hour bars, from flat: the EMAs 9 > 21 > 50 newly aligned goes long, newly aligned
the other way goes short; the alignment breaking closes the position.
Port of FMZ strategy #431286 "Triple Moving Average Channel Trend Following Strategy" (Strategy Triple Moving Average).

FMZ source id: 431286

Source
    https://www.fmz.com/strategy/431286 (PineScript v5, FMZ last modified 2023-11-06 16:58:57).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 133-230), EMA 9 / 21 / 50, exit by MA on, TP / SL off
    long_condition = ma1 > ma2 > ma3;  flat and long_condition and not long_condition[1] -> entry long (mirror short)
    long and long_condition[1] and not long_condition -> close long (mirror short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The TP / SL exits are off by default (exit_TPSL false) and not ported; the date filter is always
      true. Entries need a flat position at the bar's close, so an exit and the next entry fall on
      different bars. Opposite entries cannot occur. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA alignment.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity / close stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431286_triple_ema_alignment"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "p2": [21, 34],
    "p3": [50, 100],
}
DEFAULT_PARAMS = {"p1": 9, "p2": 21, "p3": 50}


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
    c = bars_df["close"]
    m1, m2, m3 = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("p1", "p2", "p3"))
    lc = ((m1 > m2) & (m2 > m3)).to_numpy()
    sc = ((m1 < m2) & (m2 < m3)).to_numpy()
    m = len(lc)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(1, m):
        if pos == 0:
            if lc[i] and not lc[i - 1]:
                pos = 1
            elif sc[i] and not sc[i - 1]:
                pos = -1
        elif pos == 1 and lc[i - 1] and not lc[i]:
            pos = 0
        elif pos == -1 and sc[i - 1] and not sc[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
