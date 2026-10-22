"""Three-timeframe EMA crossings, 1-hour bars: the 1-hour EMA 200 crossing the 2-hour EMA 200 flips long or short; the 3-hour EMA 10 crossing the 1-hour EMA 200 adds an entry in the trend's direction or
closes the opposite position; reversing.
Port of FMZ strategy #440345 "Dual Moving Average Crossover Trading Strategy" (ALGO 3-1-2).

FMZ source id: 440345

Source
    https://www.fmz.com/strategy/440345 (PineScript v3, FMZ last modified 2024-01-29 15:11:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 146-202), MA1 = EMA 10 on 180 minutes, MA2 = EMA 200 on 60 minutes (the chart), MA3 = EMA 200 on 120 minutes
    MA23 crossover -> close go Short, entry go Long;  MA23 crossunder -> close go Long, entry go Short
    MA12 crossover: MA2 >= MA3 -> entry go Long, MA2 <= MA3 -> close go Short;  MA12 crossunder: MA2 >= MA3 -> close go Long, MA2 <= MA3 -> entry go Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-3 security() without lookahead is read as the last completed higher bar: MA1 is the EMA
      10 of the 3-hour closes and MA3 the EMA 200 of the 2-hour closes, each from the last completed
      higher bar (UTC multiples), built from the module's own bars; MA2 is on the chart's own timeframe.
      The calls run in the written order; a close acts only on the position held, and one written after a
      reversing entry leaves the reversal standing (as #438020). Labels and alerts are not ported.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; higher-timeframe values from completed bars.
    2 generic: PASS, EMA crossings across timeframes.
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

NAME = "fmz_440345_three_timeframe_ema_crossings"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1_len": [10, 20],
    "ma23_len": [200, 100],
}
DEFAULT_PARAMS = {"ma1_len": 10, "ma23_len": 200, "tf1": "3h", "tf3": "2h"}


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


def _htf_ema(c, tf, n):
    """EMA n of the closes of tf bars (UTC multiples), the last completed tf bar's value on each bar."""
    lab = c.index.floor(tf)
    hc = c.groupby(lab).last()
    e = hc.ewm(span=n, adjust=False).mean().shift(1).reindex(lab)
    return pd.Series(e.to_numpy(), index=c.index)


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
    n23 = int(p["ma23_len"])
    ma1 = _htf_ema(c, p["tf1"], int(p["ma1_len"]))
    ma2 = c.ewm(span=n23, adjust=False).mean()
    ma3 = _htf_ema(c, p["tf3"], n23)

    def xo(x, y):
        return ((x > y) & (x.shift(1) <= y.shift(1))).to_numpy()

    a_up, a_dn = xo(ma2, ma3), xo(ma3, ma2)
    b_up, b_dn = xo(ma1, ma2), xo(ma2, ma1)
    ge, le_ = (ma2 >= ma3).to_numpy(), (ma2 <= ma3).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if a_up[i]:
            if pos == -1 and new == -1:
                new = 0
            new = 1
        if a_dn[i]:
            if pos == 1 and new == 1:
                new = 0
            new = -1
        if b_up[i]:
            if ge[i]:
                new = 1
            if le_[i] and pos == -1 and new == -1:
                new = 0
        if b_dn[i]:
            if ge[i] and pos == 1 and new == 1:
                new = 0
            if le_[i]:
                new = -1
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
