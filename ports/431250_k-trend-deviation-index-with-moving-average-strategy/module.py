"""Hull-smoothed true strength index of the open, 30-minute bars: its HMA 7 signal rising with the open above the previous
open goes long; falling with the open below the previous open goes short.
Port of FMZ strategy #431250 "趋势偏离指标K线结合移动平均线波浪策略Trend-Deviation-Index-with-Moving-Average-Strategy" (TSIHULLBOT).

FMZ source id: 431250

Source
    https://www.fmz.com/strategy/431250 (PineScript v4, FMZ last modified 2023-11-06 14:46:40).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 137-173), source open, HMA 50 / 50, signal HMA 7
    pc = change(open); tsi = 500 hma(hma(pc, 50), 50) / hma(hma(|pc|, 50), 50); line = 5 hma(tsi, 7)
    line > line[1] and open > open[1] -> entry long;  line < line[1] and open < open[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source is the bar's open, as written (known at the bar's start). HMA = wma(2 wma(x, n / 2)
      - wma(x, n), round(sqrt n)). The upper / lower lines are plot-only.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a ratio of smoothed price changes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
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

NAME = "fmz_431250_hull_tsi_open"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 25],
    "signal": [7, 14],
}
DEFAULT_PARAMS = {"length": 50, "signal": 7}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: (a * w).sum() / w.sum(), raw=True)


def _hma(x, n):
    return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(round(np.sqrt(n))))


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
    o = bars_df["open"]
    n = int(p["length"])
    pc = o.diff()
    tsi = 500 * _hma(_hma(pc, n), n) / _hma(_hma(pc.abs(), n), n)
    line = 5 * _hma(tsi, int(p["signal"]))
    lg = ((line > line.shift(1)) & (o > o.shift(1))).to_numpy()
    sh = ((line < line.shift(1)) & (o < o.shift(1))).to_numpy()
    m = len(lg)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if lg[i]:
            pos = 1
        elif sh[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
