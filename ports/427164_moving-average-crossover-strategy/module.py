"""Moving averages testing: the close crossing above SMA 20 goes long, the close crossing under
SMA 30 goes short (each entry reverses the other side; both sides on, so no separate closes).
Port of FMZ strategy #427164 "Moving Average Crossover Strategy".

FMZ source id: 427164

Source
    https://www.fmz.com/strategy/427164 (PineScript v4, FMZ last modified 2023-09-18 17:35:37).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 201-242), long "price x MA1", short "price x MA2",
MA1 SMA 20, MA2 SMA 30, longs and shorts on
    crossover(close, ma_1) -> entry long; crossunder(close, ma_2) -> entry short
    (strategy.close only when one side is switched off: never with the defaults)

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding = 2: a repeated same-direction cross while in a position is a second unit, i.e.
      sizing (criterion 4, stored); the port holds one position.
    * The month / year inputs are the author's backtest window (in_time is the constant true).
    * `ma_type` 1 = SMA for both averages (the defaults), 2 = EMA for both.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders (calc_on_every_tick false).
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 50 % of equity per unit and pyramiding 2 stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: DG427164 (2 members, with #437546, Jaccard 0.971); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427164_price_ma_cross"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1_len": [20, 10],
    "ma2_len": [30, 50],
    "ma_type": [1, 2],
}
DEFAULT_PARAMS = {"ma1_len": 20, "ma2_len": 30, "ma_type": 1}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    if int(p["ma_type"]) == 2:
        ma1 = c.ewm(span=int(p["ma1_len"]), adjust=False).mean()
        ma2 = c.ewm(span=int(p["ma2_len"]), adjust=False).mean()
    else:
        ma1, ma2 = c.rolling(int(p["ma1_len"])).mean(), c.rolling(int(p["ma2_len"])).mean()
    long_c = ((c > ma1) & (c.shift(1) <= ma1.shift(1))).to_numpy()
    short_c = ((c < ma2) & (c.shift(1) >= ma2.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
