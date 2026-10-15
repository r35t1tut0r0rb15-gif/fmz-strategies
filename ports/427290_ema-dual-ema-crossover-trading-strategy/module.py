"""2-EMA trend: with EMA 13 and EMA 26 far enough apart, a close above a rising pair (close > EMA 13
> EMA 26) goes long and a close below a falling pair goes short; a close back across EMA 13 closes
the position.
Port of FMZ strategy #427290 "Dual EMA Crossover Trading Strategy".

FMZ source id: 427290

Source
    https://www.fmz.com/strategy/427290 (PineScript v3, FMZ last modified 2023-09-19 19:36:03).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 162-184), diff minimum 0.95 %, EMA 13 / 26
    orderCondition = percent gap between the two EMAs > 0.95
    close > ema13 > ema26 and orderCondition -> entry long; close < ema13 < ema26 and orderCondition -> entry short
    close > ema13 -> close short; close < ema13 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 0.95 % gap between the averages becomes |EMA 13 - EMA 26| > `diff_atr` x
      Wilder ATR(14) (a percent distance, as worker A ported envelopes; on the source's 4-hour BTC
      bars 0.95 % is about one ATR).
    * strategy.entry reverses: REVERSAL INTENDED; the opposite entry wins over a same-bar close.
    * FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, percent gap -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and commission stored in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: DG427290 (2 members, with #430132, Jaccard 1.000, not an exact duplicate in
      the screen); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427290_two_ema_gap_trend"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "diff_atr": [1.0, 0.5, 2.0],
    "long_ema": [26, 50],
}
DEFAULT_PARAMS = {"small_ema": 13, "long_ema": 26, "diff_atr": 1.0, "atr_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars, n):
    pc = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(), (bars["low"] - pc).abs()],
                   axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def _positions(long_c, long_x, short_c, short_x):
    """Pine order semantics on completed bars: from flat an entry opens; an opposite entry reverses;
    a close exits the side held; the opposite entry wins over a close; long is tested first."""
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
    e1 = c.ewm(span=int(p["small_ema"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    gap = (e1 - e2).abs() > p["diff_atr"] * _atr(bars_df, int(p["atr_length"]))
    long_c = ((c > e1) & (e1 > e2) & gap).to_numpy()
    short_c = ((c < e1) & (e1 < e2) & gap).to_numpy()
    tgt = _positions(long_c, (c < e1).to_numpy(), short_c, (c > e1).to_numpy())
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
