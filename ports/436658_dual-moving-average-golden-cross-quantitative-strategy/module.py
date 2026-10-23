"""Hourly bars, from flat: a 3-bar Hull line turning up while below the VWMA 42 goes long, turning down while above it goes short; the Hull line turning against the position closes it.
Port of FMZ strategy #436658 "Dual Moving Average Golden Cross Quantitative Strategy" (Indicator420 strategy (SeaSide420)).

FMZ source id: 436658

Source
    https://www.fmz.com/strategy/436658 (PineScript v4, FMZ last modified 2023-12-26 17:02:29).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 188-230), HullMA 420 (plot only), HullMA cross 3, VWMA 14 / 28 / 42
    n1 = wma(2 wma(close, 2) - wma(close, 3), 2);  n2 = the same of close[1];  closelong = n1 < n2 -> close Long;  closeshort = n1 > n2 -> close Short
    n1 > n2 and opentrades < 1 and n1 < vwma(close, 42) -> entry Long;  n1 < n2 and opentrades < 1 and n1 > vwma(close, 42) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * round(z / 2) is round(3 / 2) = 1 under v4 integer division, so the fast leg is wma(close, 1) =
      close (as the other v4 ports). n2 is n1 one bar back (the same Hull of close[1]), so "n1 > n2" is
      the Hull rising. The closes come
      before the entries, and opentrades still counts the position the close has not yet filled, so a
      position is never reversed in one bar: the new side opens from flat on a later bar, as written. The
      420-bar Hull and the VWMA 14 / 28 only feed plots. No sizing code. Opposite entries cannot occur
      (entries only from flat). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, short Hull turns against a VWMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the filter vwma(close, 42); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436658_hull3_turn_vwma42_filter_flat_only"
FAMILY = "hull_ma"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "z": [3, 5],
    "a": [14, 20],
}
DEFAULT_PARAMS = {"z": 3, "a": 14}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    z = int(p["z"])
    sq = int(round(np.sqrt(z)))
    n1 = _wma(2 * _wma(c, max(z // 2, 1)) - _wma(c, z), sq)        # round(z / 2): integer division in v4
    n2 = n1.shift(1)
    na_ = int(round(int(p["a"]) * 3))
    vs = v.rolling(na_).sum()
    vw3 = (c * v).rolling(na_).sum() / vs.where(vs != 0)
    up = (n1 > n2).to_numpy()
    dn = (n1 < n2).to_numpy()
    below = (n1 < vw3).to_numpy()
    above = (n1 > vw3).to_numpy()
    m = len(up)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        start = pos
        if pos == 1 and dn[i]:
            lx[i], pos = True, 0
        elif pos == -1 and up[i]:
            sx[i], pos = True, 0
        if start == 0:
            if up[i] and below[i]:
                le[i], pos = True, 1
            elif dn[i] and above[i]:
                se[i], pos = True, -1
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
