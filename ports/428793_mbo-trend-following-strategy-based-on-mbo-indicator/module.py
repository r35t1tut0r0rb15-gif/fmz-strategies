"""HPotter TFS MBO, hourly bars: the SMA 25 minus SMA 200 spread above its own 18-bar SMA holds a long, below
it holds a short.
Port of FMZ strategy #428793 "基于MBO指标的趋势跟随策略Trend-Following-Strategy-Based-on-MBO-Indicator" (TFS: MBO Backtest).

FMZ source id: 428793

Source
    https://www.fmz.com/strategy/428793 (PineScript v2, FMZ last modified 2023-10-09 15:22:04).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 244-260), fast 25, slow 200, length 18, reverse false
    nMBO = sma(close,25) - sma(close,200); xSMAMBO = sma(nMBO, 18)
    pos = nMBO > xSMAMBO ? 1 : nMBO < xSMAMBO ? -1 : pos[1]; pos 1 -> entry long; -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Trade reverse" defaults to false and is fixed.
    * strategy.entry reverses: REVERSAL INTENDED; same-direction entries while in a position are
      ignored (pyramiding 0). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a comparison of two series in the same units.
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

NAME = "fmz_428793_tfs_mbo"
FAMILY = "macd_momentum"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [25, 12],
    "length": [18, 9],
}
DEFAULT_PARAMS = {"fast": 25, "slow": 200, "length": 18}


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
    mbo = c.rolling(int(p["fast"])).mean() - c.rolling(int(p["slow"])).mean()
    sig = mbo.rolling(int(p["length"])).mean()
    upc, dnc = (mbo > sig).to_numpy(), (mbo < sig).to_numpy()
    m = len(c)
    pos = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if upc[i]:
            q = 1
        elif dnc[i]:
            q = -1
        pos[i] = q
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(pos == 1, index=idx), false, pd.Series(pos == -1, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
