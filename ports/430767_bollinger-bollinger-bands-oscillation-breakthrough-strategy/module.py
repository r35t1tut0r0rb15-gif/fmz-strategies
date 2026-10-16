"""Bollinger basis dip with a strong Aroon up, 1-minute bars, long only: the close crossing under the 20-bar basis with
Aroon up (288) above 90 goes long; the close crossing under the upper band, or Aroon up under 70, closes the long.
Port of FMZ strategy #430767 "Bollinger带震荡型突破策略Bollinger-Bands-Oscillation-Breakthrough-Strategy" (Bollinger bands And Aroon Scalping (by Coinrule)).

FMZ source id: 430767

Source
    https://www.fmz.com/strategy/430767 (PineScript v4, FMZ last modified 2023-11-01 16:45:54).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 157-206), BB 20 / 2, Aroon 288, confirmation 90, stop 70
    AroonUP = 100 (highestbars(high, 289) + 288) / 288
    crossunder(close, basis) and AroonUP > 90 -> entry long
    crossunder(close, upper) or AroonUP < 70 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * highestbars counts back from the current bar (0 = this bar); a tie takes the most recent bar.
    * The close is written after the entry: a bar that both enters and closes ends flat when already
      long, long when flat. The 2020-2112 window is the author's: dropped.
    * The strategy() line (with process_orders_on_close) is commented out in the corpus copy: orders
      read as written (as #429505), bar-close orders. Long only; Opposite entries cannot occur.
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands and an Aroon level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out 30 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

NAME = "fmz_430767_bb_basis_aroon_scalp_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_ar": [288, 144],
    "confirmation": [90, 80],
}
DEFAULT_PARAMS = {"length_bb": 20, "mult": 2.0, "length_ar": 288, "confirmation": 90, "stop": 70}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _highestbars(x, n):
    """ta.highestbars(x, n) as a non-positive offset; a tie takes the most recent bar."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = sliding_window_view(v, n)[:, ::-1]
        out[n - 1:] = -np.argmax(w, axis=1).astype(float)
    return pd.Series(out, index=x.index)


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
    h, c = bars_df["high"], bars_df["close"]
    n = int(p["length_bb"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper = basis + p["mult"] * sd
    a = int(p["length_ar"])
    aroon_up = 100 * (_highestbars(h, a + 1) + a) / a
    bull = ((c < basis) & (c.shift(1) >= basis.shift(1))).to_numpy()
    bear = ((c < upper) & (c.shift(1) >= upper.shift(1))).to_numpy()
    entry = bull & (aroon_up > p["confirmation"]).to_numpy()
    ex = bear | (aroon_up < p["stop"]).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if entry[i]:
            pos = 1
        if ex[i] and start == 1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
