"""EMA / SMA state: EMA 13 above SMA 30 holds a long, SMA 30 above EMA 13 holds a short.
Port of FMZ strategy #427861 "Moving Average Cross EMA SMA Strategy".

FMZ source id: 427861

Source
    https://www.fmz.com/strategy/427861 (PineScript v3, FMZ last modified 2023-09-26 11:27:47).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 164-212), EMA 13, SMA 30
    enterLong = ema(close, 13) > sma(close, 30) -> entry long (every such bar)
    exitLong = sma > ema -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "slower" VWMA and the RSI are computed but only drawn: they reach no order.
    * An entry on the side already held is ignored (pyramiding 0): the port holds the state.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8); the VWMA is drawn only.
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427861_ema_sma_state"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [13, 8],
    "slow": [30, 50],
}
DEFAULT_PARAMS = {"fast": 13, "slow": 30}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean().to_numpy()
    s = c.rolling(int(p["slow"])).mean().to_numpy()
    m = len(f)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if f[i] > s[i]:
            pos = 1
        elif s[i] > f[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
