"""HPotter z-score side, 15-minute bars: the close's 20-bar z-score above 0 goes long, below 0 goes short; the position
reverses on the opposite sign.
Port of FMZ strategy #434552 "Z Score Price Breakout Strategy" (Z-Score Strategy).

FMZ source id: 434552

Source
    https://www.fmz.com/strategy/434552 (PineScript v2, FMZ last modified 2023-12-07 15:17:43).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 153-168), period 20, trigger 0, reverse false
    z = (close - sma(close, 20)) / stdev(close, 20);  pos = z > 0 ? 1 : z < 0 ? -1 : pos[1];  pos 1 -> entry long;  pos -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * stdev is the population one. A zero deviation gives no z (held). strategy.entry reverses:
      REVERSAL INTENDED. reverse is false. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a z-score.
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

NAME = "fmz_434552_zscore_side"
FAMILY = "zscore_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [20, 50],
    "trigger": [0.0, 1.0],
}
DEFAULT_PARAMS = {"period": 20, "trigger": 0.0}


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
    n = int(p["period"])
    z = (c - c.rolling(n).mean()) / c.rolling(n).std(ddof=0).replace(0.0, np.nan)
    tr = float(p["trigger"])
    up, dn = (z > tr).to_numpy(), (z < tr).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
