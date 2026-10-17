"""SMA 20 / 40 crosses with an RSI side filter, 3-hour bars: a golden cross closes a short and goes long when the RSI 14 is
above 50; a death cross closes a long and goes short when the RSI is below 50.
Port of FMZ strategy #434167 "Bitcoin MA Crossover Strategy" (Bitcoin - MA Crossover Strategy).

FMZ source id: 434167

Source
    https://www.fmz.com/strategy/434167 (PineScript v4, FMZ last modified 2023-12-04 13:55:45).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 161-197), SMA 20 / 40, RSI 14, equity risk 10 %
    crossover(sma20, sma40) -> close a short (strategy.order of its size);  and rsi > 50 -> entry long (units)
    crossunder(sma20, sma40) -> close a long;  and rsi < 50 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are strategy.order calls of the open size in the other direction, i.e. closes; a cross
      without its RSI confirmation only closes. The unit count (10 % of equity) is sizing.
    * REVERSAL INTENDED. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crosses and an RSI side filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-risk unit count stored in original_sizing.txt.
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

NAME = "fmz_434167_sma_cross_rsi_filter"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [40, 80],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 40, "rsi_len": 14}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = ((100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())).to_numpy()
    xo = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    xu = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if xo[i]:
                pos = 1 if r[i] > 50 else (0 if pos == -1 else pos)
            elif xu[i]:
                pos = -1 if r[i] < 50 else (0 if pos == 1 else pos)
            tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
