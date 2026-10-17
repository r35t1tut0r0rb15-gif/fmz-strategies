"""SMA 377 / 200 crosses, 5-minute bars, as written: the SMA 377 crossing above the SMA 200 goes long; the SMA 200 crossing
above the SMA 377 goes short; always in after the first cross.
Port of FMZ strategy #433020 "Dual SMA Crossover Strategy" (SMA Strategy (melihtuna)).

FMZ source id: 433020

Source
    https://www.fmz.com/strategy/433020 (PineScript v4, FMZ last modified 2023-11-23 16:42:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 137-169), smaB1 377, smaB2 200, smaS1 377, smaS2 200; window from 2020
    crossover(sma(close, 377), sma(close, 200)) -> entry long;  crossover(sma(close, 200), sma(close, 377)) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the long side buys when the slower average crosses above the faster one (a
      contrarian cross); the buy and sell pairs share the same lengths by default, so one grid pair
      drives both.
    * strategy.entry reverses: REVERSAL INTENDED. The date window (from 2020) is dropped. FREQ =
      "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and the commission stored.
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

NAME = "fmz_433020_sma_377_200_cross"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len_a": [377, 500],
    "len_b": [200, 100],
}
DEFAULT_PARAMS = {"len_a": 377, "len_b": 200}


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
    a = c.rolling(int(p["len_a"])).mean()
    b = c.rolling(int(p["len_b"])).mean()
    up = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    dn = ((b > a) & (b.shift(1) <= a.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(x, index=bars_df.index)
                 for x in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
