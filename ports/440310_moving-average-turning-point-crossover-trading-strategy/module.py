"""SMA 25 / 50 crossings with turning-point exits, 1-hour bars: the SMA 25 crossing over the SMA 50 goes long, under it short (reversing); a short closes when the SMA 25's one-bar change turns up through
+0.02 %, a long when it turns down through -0.02 %.
Port of FMZ strategy #440310 "Moving Average Turning Point Crossover Trading Strategy" (MA Crossover Strategy with MA Turning Point Exits).

FMZ source id: 440310

Source
    https://www.fmz.com/strategy/440310 (PineScript v4, FMZ last modified 2024-01-29 11:15:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 150-213), source close; MA 1 SMA 25, MA 2 SMA 50; look-back 1; minimum slope 2 x 0.01 (percent)
    crossover(ma1, ma2) -> entry Long;  crossunder(ma1, ma2) -> entry Short;  roc1 = roc(ma1, 1);  crossover(roc1, 0.02) -> ma1up, not ma1down;  crossunder(roc1, -0.02) -> ma1down, not ma1up
    ma1up and ma1down[1] -> close Short;  ma1down and ma1up[1] -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The security call is on the chart's own timeframe, so price is the close. roc is in percent, so
      the 0.02 threshold is 0.02 %. The turning flags hold until the opposite crossing; a close acts
      only on the position held, and one written after a reversing entry leaves the reversal standing
      (as #438020). strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings and slope turns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430020 (4 members, best partner #436860, Jaccard 0.768); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440310_sma25_50_cross_turning_point_exit"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [25, 10],
    "ma2": [50, 100],
}
DEFAULT_PARAMS = {"ma1": 25, "ma2": 50, "lookback": 1, "strength": 0.02}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a = c.rolling(int(p["ma1"])).mean()
    b = c.rolling(int(p["ma2"])).mean()
    L = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    S = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    k = int(p["lookback"])
    roc = 100 * (a - a.shift(k)) / a.shift(k)
    th = float(p["strength"])
    r_up = ((roc > th) & (roc.shift(1) <= th)).to_numpy()
    r_dn = ((roc < -th) & (roc.shift(1) >= -th)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    up = down = False
    for i in range(m):
        new = pos
        if L[i]:
            new = 1
        if S[i]:
            new = -1
        up_p, down_p = up, down
        if r_up[i]:
            up, down = True, False
        if r_dn[i]:
            up, down = False, True
        if up and down_p and pos == -1 and new == -1:
            new = 0
        if down and up_p and pos == 1 and new == 1:
            new = 0
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
