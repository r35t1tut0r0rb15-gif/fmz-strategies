"""Average of five SMAs, 30-minute bars: with the close above the mean of the SMAs 8 / 21 / 50 / 100 / 200 and that mean
rising the strategy goes long; with the close below it and the mean falling it goes short; otherwise it keeps its
position.
Port of FMZ strategy #433560 "Multi-SMA均线交叉策略Multi-SMA-Moving-Average-Crossover-Strategy" (STRATEGY AVERAGE MULTI_SMA).

FMZ source id: 433560

Source
    https://www.fmz.com/strategy/433560 (PineScript v3, FMZ last modified 2023-11-28 15:08:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 115-164), SMA 8 / 21 / 50 / 100 / 200
    media = (sma8 + sma21 + sma50 + sma100 + sma200) / 5
    close > media and media > media[1] -> entry long ("BUY");  close < media and media < media[1] -> entry short ("SELL") (each written twice)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are levels (a repeat in the same direction is ignored). strategy.entry reverses:
      REVERSAL INTENDED. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, the close against an average and its slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433560_five_sma_mean_trend"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "scale": [1.0, 2.0],
}
DEFAULT_PARAMS = {"scale": 1.0}


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
    s = float(p["scale"])
    media = sum(c.rolling(int(round(n * s))).mean() for n in (8, 21, 50, 100, 200)) / 5
    lc = ((c > media) & (media > media.shift(1))).to_numpy()
    sc = ((c < media) & (media < media.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if lc[i]:
            pos = 1
        elif sc[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
