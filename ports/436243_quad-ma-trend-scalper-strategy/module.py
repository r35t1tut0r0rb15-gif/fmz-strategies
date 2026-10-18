"""Four-average trend scalper, 1-hour bars: the 13-bar average crossing over the 21-bar one while it is over the long average (EMA 84) goes long (closed when it crosses under the EMA 54);
the mirror under the long average goes short (closed when it crosses back over the EMA 54).
Port of FMZ strategy #436243 "Quad MA Trend Scalper Strategy" (Quad MA Trend Scalper Backtest).

FMZ source id: 436243

Source
    https://www.fmz.com/strategy/436243 (PineScript v3, FMZ last modified 2023-12-22 14:25:04).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 161-211), SMA 13 / 21; EMA 54 / 84 (the long pair); pyramiding 100
    crossover(ma1, ma2) and ma1 > ma4 -> entry long;  crossunder(ma1, ma3) -> close long;  crossunder(ma1, ma2) and ma1 < ma4 -> entry short;  crossover(ma1, ma3) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The fourth average is the EMA 84 when the long-exponential switch is on (the off branch repeats
      the first long length, a script slip not used by the default). The extra entries (pyramiding 100) are sizing.
      The four orders of one bar are filled in the script's call order at the next open. REVERSAL INTENDED.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the pyramiding input stored.
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

NAME = "fmz_436243_quad_ma_trend_scalper"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length1": [13, 8],
    "length2": [21, 34],
}
DEFAULT_PARAMS = {"length1": 13, "length2": 21, "longlength1": 54, "longlength2": 84}


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
    c = bars_df["close"]
    ma1, ma2 = c.rolling(int(p["length1"])).mean(), c.rolling(int(p["length2"])).mean()
    ma3 = c.ewm(span=int(p["longlength1"]), adjust=False).mean()
    ma4 = c.ewm(span=int(p["longlength2"]), adjust=False).mean()
    xo = lambda a, b: ((a > b) & (a.shift(1) <= b.shift(1))).fillna(False).to_numpy()   # noqa: E731
    xu = lambda a, b: ((a < b) & (a.shift(1) >= b.shift(1))).fillna(False).to_numpy()   # noqa: E731
    e_l = xo(ma1, ma2) & (ma1 > ma4).fillna(False).to_numpy()
    c_l = xu(ma1, ma3)
    e_s = xu(ma1, ma2) & (ma1 < ma4).fillna(False).to_numpy()
    c_s = xo(ma1, ma3)
    m = len(e_l)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    pend = None
    for i in range(m):
        if i > 0 and pend is not None:          # fills at this bar's open, in the script's call order
            a, b, cc, d = pend
            if a and pos <= 0:
                pos = 1
            if b and pos == 1:
                pos = 0
            if cc and pos >= 0:
                pos = -1
            if d and pos == -1:
                pos = 0
        held[i] = pos
        pend = (bool(e_l[i]), bool(c_l[i]), bool(e_s[i]), bool(c_s[i]))
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
