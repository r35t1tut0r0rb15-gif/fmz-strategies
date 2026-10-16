"""Volatility range breakout [wbburgin]: bands at the close +- the close x its 100-bar range ratio,
averaged over 100 bars; a high crossing above the upper band goes long, a low crossing under the lower
band goes short; the close crossing the bands' mid-line closes the position.
Port of FMZ strategy #427507 "Volatility Range Breakout Trading Strategy".

FMZ source id: 427507

Source
    https://www.fmz.com/strategy/427507 (PineScript v5, FMZ last modified 2023-09-21 20:38:29).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 212-263), average 100, volatility 100, exit "Volatility MA"
    vx = 2 (highest(close, 100) - lowest(close, 100)) / (highest + lowest)
    hb = wma(close + close vx, 100, vx); lb = wma(close - close vx, 100, vx); mid = (hb + lb) / 2
    crossover(high, hb) -> entry long; crossunder(close, mid) -> close long
    crossunder(low, lb) -> entry short; crossover(close, mid) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's own wma(x, n, w) uses ONE weight (the current bar's vx) for all n terms, so it is
      the simple average of x over n bars (the weight cancels): ported as such (na when vx is 0).
    * pyramiding 20: repeated same-direction entries are adds (sizing, stored); one position.
    * The "Range Crossover" exit type is not the default: the grid tries it (`exit_type` 2).
    * strategy.entry reverses: REVERSAL INTENDED; entries win over same-bar closes.
    * FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bands as fractions of price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 20 stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427507_volatility_range_breakout"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "avg_length": [100, 50],
    "vol_length": [100, 50],
    "exit_type": [1, 2],
}
DEFAULT_PARAMS = {"avg_length": 100, "vol_length": 100, "exit_type": 1}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _positions(long_c, long_x, short_c, short_x):
    m = len(long_c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        elif pos == 1 and long_x[i]:
            pos = 0
        elif pos == -1 and short_x[i]:
            pos = 0
        tgt[i] = pos
    return tgt


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
    nv, na_ = int(p["vol_length"]), int(p["avg_length"])
    hh, ll = c.rolling(nv).max(), c.rolling(nv).min()
    vx = 2 * (hh - ll) / (hh + ll)
    hb = (c + c * vx).rolling(na_).mean().where(vx != 0)
    lb = (c - c * vx).rolling(na_).mean().where(vx != 0)
    mid = (hb + lb) / 2
    h, lo = bars_df["high"], bars_df["low"]

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    def xu(a, b):
        return (a < b) & (a.shift(1) >= b.shift(1))

    long_c, short_c = xo(h, hb), xu(lo, lb)
    if int(p["exit_type"]) == 2:
        long_x, short_x = xu(c, hb), xo(c, lb)
    else:
        long_x, short_x = xu(c, mid), xo(c, mid)
    tgt = _positions(long_c.to_numpy(), long_x.to_numpy(), short_c.to_numpy(), short_x.to_numpy())
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
