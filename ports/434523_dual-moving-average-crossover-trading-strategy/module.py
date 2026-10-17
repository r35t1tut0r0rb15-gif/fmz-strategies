"""Price against three EMAs, 1-minute bars: a close above the EMA 50, 144 and 200 goes long, a close below all three goes
short; held otherwise and reversed on the opposite state.
Port of FMZ strategy #434523 "Dual Moving Average Crossover Trading Strategy" (EMA Crossover Strategy).

FMZ source id: 434523

Source
    https://www.fmz.com/strategy/434523 (PineScript v5, FMZ last modified 2023-12-07 10:36:46).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 153-176), EMA 50 / 144 / 200
    close > ema50 and close > ema144 and close > ema200 -> entry long;  close below all three -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price against averages.
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

NAME = "fmz_434523_three_ema_side"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 20],
    "slow": [200, 400],
}
DEFAULT_PARAMS = {"fast": 50, "mid": 144, "slow": 200}


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
    e = [c.ewm(span=int(p[k]), adjust=False).mean() for k in ("fast", "mid", "slow")]
    lc = ((c > e[0]) & (c > e[1]) & (c > e[2])).to_numpy()
    sc = ((c < e[0]) & (c < e[1]) & (c < e[2])).to_numpy()
    m = len(lc)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if lc[i]:
            q = 1
        elif sc[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
