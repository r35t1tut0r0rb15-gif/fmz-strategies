"""HPotter's volume state against its SMA 20, 3-hour bars: volume under its average goes long, volume over it goes short (the state holds on a tie); reversing.
Port of FMZ strategy #428967 "Hidden Gap Volume Strategy" (Hidden Gap`s VSA Volume).

FMZ source id: 428967

Source
    https://www.fmz.com/strategy/428967 (PineScript v2, FMZ last modified 2023-10-11 14:44:26).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 171-194), volume SMA 20 (the 40 / 2 / 20-bar extremes only colour the bars); reverse off
    pos = volume > sma(volume, 20) ? -1 : volume < sma(volume, 20) ? 1 : pos[1]
    pos == 1 -> entry Long;  pos == -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Quiet volume is read as long and heavy volume as short, as written. The highest / lowest volume
      windows only colour the bars. REVERSAL INTENDED. No sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume against its average as a state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against sma(volume, 20); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428967_volume_vs_sma20_state_reversal"
FAMILY = "volume_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_ma": [20, 50],
}
DEFAULT_PARAMS = {"length_ma": 20}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    v = bars_df["volume"]
    sma = v.rolling(int(p["length_ma"])).mean()
    raw = np.where(v > sma, -1, np.where(v < sma, 1, 0))
    pos = np.zeros(len(raw), dtype=np.int8)
    q = 0
    for i in range(len(raw)):
        if raw[i] != 0:
            q = raw[i]
        pos[i] = q
    prev = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((pos == 1) & (prev != 1), index=ix), false,
            pd.Series((pos == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
