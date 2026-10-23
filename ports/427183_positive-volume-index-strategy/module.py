"""HPotter's Positive Volume Index (the running sum of the close's 1-bar rate of change on bars whose volume rose) against its EMA 255, 3-hour bars: the index above its EMA goes long, below goes short; reversing.
Port of FMZ strategy #427183 "Positive Volume Index Strategy" (Positive Volume Index).

FMZ source id: 427183

Source
    https://www.fmz.com/strategy/427183 (PineScript v2, FMZ last modified 2023-09-18 21:21:54).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 165-178), EMA 255; reverse off
    nRes = volume > volume[1] ? nRes[1] + roc(close, 1) : nRes[1]  (from 0);  pos = nRes > ema(nRes, 255) ? 1 : nRes < ema ? -1 : pos[1]
    pos == 1 -> entry Long;  pos == -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The index starts at 0 and runs from the first loaded bar (its level depends on the start, the
      comparison with its own EMA does not much). REVERSAL INTENDED. No sizing code. FREQ = "3h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, positive volume index against its EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: DG427183 (2 members, best partner #436111, Jaccard 0.901); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the PVI rule volume > volume[1]; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427183_positive_volume_index_ema255_state_reversal"
FAMILY = "volume_index"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [255, 100],
}
DEFAULT_PARAMS = {"ema_len": 255}


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
    c, v = bars_df["close"], bars_df["volume"]
    roc = (100 * (c - c.shift(1)) / c.shift(1)).fillna(0.0)
    nres = roc.where(v > v.shift(1), 0.0).cumsum()
    ema = nres.ewm(span=int(p["ema_len"]), adjust=False).mean()
    raw = np.where(nres > ema, 1, np.where(nres < ema, -1, 0))
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
