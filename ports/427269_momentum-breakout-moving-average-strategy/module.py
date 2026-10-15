"""Mbit moving average, contrarian: after exactly 27 consecutive closes below the SMA 520 go long,
after exactly 27 consecutive closes above it go short (always in the market after the first signal).
Port of FMZ strategy #427269 "Momentum Breakout Moving Average Strategy".

FMZ source id: 427269

Source
    https://www.fmz.com/strategy/427269 (PineScript v5, FMZ last modified 2023-09-19 16:33:13).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 156-180), length 520, confirm bars 27
    bcount = close > sma ? bcount[1] + 1 : 0; scount = close < sma ? scount[1] + 1 : 0
    scount == 27 -> entry long; bcount == 27 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written: the 27th close BELOW the average buys and the 27th close ABOVE it sells.
    * The counts start from bar 1 (nz); bars before the SMA exists compare with na (false): 0.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bar counts only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427269_mbit_ma_count_fade"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [520, 260, 1040],
    "confirm_bars": [27, 13],
}
DEFAULT_PARAMS = {"length": 520, "confirm_bars": 27}


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
    ma = c.rolling(int(p["length"])).mean()
    above, below = (c > ma).to_numpy(), (c < ma).to_numpy()
    k = int(p["confirm_bars"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    bc = sc = 0
    pos = 0
    for i in range(m):
        bc = bc + 1 if above[i] else 0
        sc = sc + 1 if below[i] else 0
        if sc == k and pos != 1:
            pos = 1
        elif bc == k and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
