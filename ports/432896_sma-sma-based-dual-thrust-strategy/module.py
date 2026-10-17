"""SMA 20 high / low channel breaks, 10-minute bars: the close crossing above the SMA 20 of the highs goes long, crossing
below 99 % of it closes the long; the close crossing below the SMA 20 of the lows goes short, crossing above 101 % of
the SMA of the highs closes the short.
Port of FMZ strategy #432896 "基于SMA的多空策略SMA-Based-Dual-Thrust-Strategy" (ma 20 high-low).

FMZ source id: 432896

Source
    https://www.fmz.com/strategy/432896 (PineScript v4, FMZ last modified 2023-11-22 15:42:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 144-177), SMA 20 of highs / lows, exits 0.99 / 1.01 x the SMA of the highs
    crossover(close, smaH) -> entry long;  crossunder(close, smaL) -> entry short
    crossunder(close, 0.99 smaH) -> close long;  crossover(close, 1.01 smaH) -> close short (both on the SMA of the highs, as written)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both exit lines use the SMA of the highs, as written. The closes are written after the entries
      and act on the position held at the bar's start; an opposite entry reverses and is not undone.
      The start date (2015-06-01) is the author's window: dropped. REVERSAL INTENDED. FREQ = "10min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel crosses and percentage offsets.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 stored in original_sizing.txt.
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

NAME = "fmz_432896_sma_high_low_channel"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "offset": [1.0, 0.5],
}
DEFAULT_PARAMS = {"length": 20, "offset": 1.0}


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
    n = int(p["length"])
    sh, sl = h.rolling(n).mean(), lo.rolling(n).mean()
    f = float(p["offset"]) / 100
    xu = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))  # noqa: E731
    el = xu(c, sh).to_numpy()
    es = xu(sl, c).to_numpy()
    xl = xu(sh * (1 - f), c).to_numpy()
    xs = xu(c, sh * (1 + f)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if el[i]:
            pos = 1
        if es[i]:
            pos = -1
        if xl[i] and start == 1 and pos == 1:
            pos = 0
        if xs[i] and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
