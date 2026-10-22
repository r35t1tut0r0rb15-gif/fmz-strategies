"""30-bar comparisons, 2-hour bars, long only: the 30-bar high at or over the close 30 bars ago buys; the previous close over the close 30 bars ago sells.
Port of FMZ strategy #458128 "Three Week High Low Momentum Trading Strategy" (Buy and Sell Strategy (30-bar high vs close 30 bars ago)).

FMZ source id: 458128

Source
    https://www.fmz.com/strategy/458128 (PineScript v5, FMZ last modified 2024-07-30 10:44:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 197-233), highest(high, 30) (current bar included); close[1]; close[30]
    highest(high, 30) >= close[30] -> entry Buy;  close[1] > close[30] -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both tests hold on most bars. The entry is called before the close; the close acts only on a long
      held into the bar, so a held long closes and the next bar buys again, as written. Long only. No
      sizing code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, 30-bar high and close comparisons.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458128_high30_vs_close30_buy_close1_sell_long"
FAMILY = "momentum_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [30, 15],
}
DEFAULT_PARAMS = {"lookback": 30}


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
    h, c = bars_df["high"], bars_df["close"]
    n = int(p["lookback"])
    ref = c.shift(n)
    buy = (h.rolling(n).max() >= ref).to_numpy()
    sell = (c.shift(1) > ref).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        cur = pos
        if buy[i] and pos == 0:
            cur = 1
        if sell[i] and pos == 1:
            cur = 0                              # the close acts only on a long held into the bar
        if cur == 1 and pos == 0:
            le[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        pos = cur
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
