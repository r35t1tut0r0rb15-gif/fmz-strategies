"""Close above / below both the EMA 9 and the SMA 20, 1-hour bars: a close above both goes long, below both goes short; the close crossing over either average closes every position.
Port of FMZ strategy #439353 "Exponential Moving Average and Moving Average Crossover with Close Strategy" (EMA and MA Crossover with Close Strategy).

FMZ source id: 439353

Source
    https://www.fmz.com/strategy/439353 (PineScript v4, FMZ last modified 2024-01-19 14:50:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 163-197), EMA 9, SMA 20 (fixed in the code)
    buyCondition = close > ema9 and close > ma20;  sellCondition = close < ema9 and close < ma20;  closeCondition = crossover(close, ema9) or crossover(close, ma20)
    if buy: entry Buy else if sell: entry Sell;  if closeCondition: close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The final close_all acts on the position held at the bar close and the bar ends flat (as #430380);
      from flat the entry opens. So a short is closed (not reversed) on the bar the close crosses back
      over an average, and a long that meets a crossover closes. A same-side entry while in a position
      is ignored. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average sides and crossings.
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

NAME = "fmz_439353_ema9_sma20_side_cross_close"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_ema": [9, 20],
    "length_ma": [20, 50],
}
DEFAULT_PARAMS = {"length_ema": 9, "length_ma": 20}


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
    e = c.ewm(span=int(p["length_ema"]), adjust=False).mean()
    s = c.rolling(int(p["length_ma"])).mean()
    buy = ((c > e) & (c > s)).to_numpy()
    sell = ((c < e) & (c < s)).to_numpy()
    ex = (((c > e) & (c.shift(1) <= e.shift(1))) | ((c > s) & (c.shift(1) <= s.shift(1)))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and pos != 1:
            new = 1
        elif sell[i] and pos != -1:
            new = -1
        if ex[i] and pos != 0:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
