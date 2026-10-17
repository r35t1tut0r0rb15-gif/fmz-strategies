"""Cloud breaks, 1-hour bars: the close moving above the top of the Ichimoku cloud drawn under it (the spans of 26 bars ago)
goes long, moving below the cloud's bottom goes short; always in once started.
Port of FMZ strategy #432358 "Ichimoku-Kinko-Hyo交易策略Ichimoku-Kinko-Hyo-Trading-Strategy" (Ichimoku system).

FMZ source id: 432358

Source
    https://www.fmz.com/strategy/432358 (PineScript v4, FMZ last modified 2023-11-16 17:31:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 167-220), Ichimoku 9 / 26 / 52, displacement 26, buy-only off; the TP / SL exits commented out
    above = max(lead1, lead2); below = min(lead1, lead2)
    close > above[26] and close[1] < above[27] -> entry long;  close < below[26] and close[1] > below[27] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spans are mid-ranges (donchian = average of the lowest low and highest high), read 26 bars
      back for the current bar and 27 for the previous one, as written. buyOnly is off, so the sell
      signal opens a short. The profit / stoploss exits are commented out.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, cloud crosses.
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

NAME = "fmz_432358_ichimoku_cloud_break"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conv": [9, 7],
    "span_b": [52, 44],
}
DEFAULT_PARAMS = {"conv": 9, "base": 26, "span_b": 52, "disp": 26}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    mid = lambda n: (lo.rolling(n).min() + h.rolling(n).max()) / 2  # noqa: E731
    l1 = (mid(int(p["conv"])) + mid(int(p["base"]))) / 2
    l2 = mid(int(p["span_b"]))
    above, below = np.maximum(l1, l2), np.minimum(l1, l2)
    d = int(p["disp"])
    x = ((c > above.shift(d)) & (c.shift(1) < above.shift(d + 1))).to_numpy()
    y = ((c < below.shift(d)) & (c.shift(1) > below.shift(d + 1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if x[i]:
            pos = 1
        if y[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
