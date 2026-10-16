"""Noro's HullMA, 4-hour bars: a rising HMA 16 goes long, a falling one goes short, but strategy.close_all() runs on every
bar, so each position is held for one bar and the next bar is flat.
Port of FMZ strategy #430853 "Hull移动平均的趋势跟踪策略Hull-Moving-Average-Trend-Following-Strategy" (Noro's HullMA Strategy).

FMZ source id: 430853

Source
    https://www.fmz.com/strategy/430853 (PineScript v3, FMZ last modified 2023-12-01 15:02:29).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 173-210), HullMA 16
    n1 = wma(2 wma(close, 8) - wma(close, 16), 4); n2 = the same on close[1] (= n1[1])
    n1 > n2 -> entry long;  n1 < n2 -> entry short;  if true -> strategy.close_all()   (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * close_all on every bar acts on the position held at the start of the bar: a position entered on
      a signal bar fills at the next open and is closed at that bar's close (filled at the open after
      it); the bar it closes takes no new position (the entries meet a held position). Ported as
      written: one-bar holds on every other bar.
    * round(16 / 2) = 8, round(sqrt(16)) = 4. The 1900-2100 window is the author's: dropped.
      strategy.entry reverses: REVERSAL INTENDED. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close_all every bar as written.
    2 generic: PASS, the slope of a Hull moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital % lot stored in original_sizing.txt.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430853_noro_hullma_one_bar"
FAMILY = "hull_ma"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [16, 32, 8],
}
DEFAULT_PARAMS = {"n": 16}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


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
    n = int(p["n"])
    diff = 2 * _wma(c, int(round(n / 2))) - _wma(c, n)
    n1 = _wma(diff, int(round(np.sqrt(n))))
    n2 = n1.shift(1)
    up, dn = (n1 > n2).to_numpy(), (n1 < n2).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if start == 0:
            pos = 1 if up[i] else (-1 if dn[i] else 0)
        else:
            pos = 0                                      # close_all on every bar
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
