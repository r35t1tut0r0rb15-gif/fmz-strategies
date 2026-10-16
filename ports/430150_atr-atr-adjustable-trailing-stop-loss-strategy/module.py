"""ATR trailing-stop line cross (ceyhun), 30-minute bars: the 10-bar highest of (high - 2.5 ATR 5) is the line; the close
crossing above it goes long, crossing below it goes short.
Port of FMZ strategy #430150 "ATR可调节跟踪止损策略ATR-Adjustable-Trailing-Stop-Loss-Strategy" (ATR Trailing Stoploss Strategy).

FMZ source id: 430150

Source
    https://www.fmz.com/strategy/430150 (PineScript v4, FMZ last modified 2023-10-25 15:08:04).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 194-215), ATR 5, HHV 10, multiplier 2.5
    TS = highest(high - 2.5 atr(5), 10)
    crossover(close, TS) -> entry long;  crossunder(close, TS) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line's second, comma-separated expression (a barssince that never assigns) has no effect:
      TS is the highest value only. The line is used as a signal level, not as a stop order.
    * ATR is Wilder's (ta.atr). strategy.entry reverses: REVERSAL INTENDED. FREQ = "30min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR line.
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

NAME = "fmz_430150_atr_trailing_line_cross"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hhv": [10, 20],
    "mult": [2.5, 3.5],
}
DEFAULT_PARAMS = {"atr": 5, "hhv": 10, "mult": 2.5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


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
    ts = (bars_df["high"] - p["mult"] * _atr(bars_df, int(p["atr"]))).rolling(int(p["hhv"])).max()
    xo = ((c > ts) & (c.shift(1) <= ts.shift(1))).to_numpy()
    xu = ((c < ts) & (c.shift(1) >= ts.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if xo[i]:
            pos = 1
        elif xu[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
