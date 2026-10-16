"""Ichimoku cloud position, 15-minute bars: the close above both cloud lines (as plotted for this bar,
i.e. computed 26 bars ago) holds a long, below both a short.
Port of FMZ strategy #428684 "Ichimoku Cloud Trading Strategy".

FMZ source id: 428684

Source
    https://www.fmz.com/strategy/428684 (PineScript v4, FMZ last modified 2023-10-08 12:24:06).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 215-242), conversion 9, base 26, span B 52, displacement 26
    lead1 = avg(donchian(9), donchian(26)); lead2 = donchian(52)
    buy = close > lead1[26] and close > lead2[26] -> entry long; sell mirrors -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The [26] lag is written into the conditions (the displacement input only moves the plots).
    * Repeated same-side entries are ignored. strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the cloud is from 26 bars ago.
    2 generic: PASS, channel lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
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

NAME = "fmz_428684_ichimoku_cloud_position"
FAMILY = "ichimoku"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion": [9, 7],
    "base": [26, 22],
}
DEFAULT_PARAMS = {"conversion": 9, "base": 26, "span_b": 52, "lag": 26}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    don = lambda n: (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2
    lead1 = (don(p["conversion"]) + don(p["base"])) / 2
    lead2 = don(p["span_b"])
    k = int(p["lag"])
    l1, l2 = lead1.shift(k), lead2.shift(k)
    buy = ((c > l1) & (c > l2)).to_numpy()
    sell = ((c < l1) & (c < l2)).to_numpy()
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if buy[i]:
            pos = 1
        elif sell[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
