"""ATH 200 breakout, long only: a close above the highest high of the previous 200 bars goes long; the
close crossing under EMA 90 closes the long.
Port of FMZ strategy #427388 "Buying Strategy Based on Historical High Breakout".

FMZ source id: 427388

Source
    https://www.fmz.com/strategy/427388 (PineScript v5, FMZ last modified 2023-09-20 15:53:26).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 161-177), ATH period 200, EMA 90
    close > highest(high, 200)[1] -> entry long (qty 1); crossunder(close, ema(close, 90)) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The high covers the 200 bars before the current one ([1]). The EMA input's default (90) is
      below its own minval (100); the default is what runs.
    * Long only; entries only from flat (pyramiding 0); one signal per bar.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bar counts only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 stored in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427388_ath_200_breakout_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bars": [200, 100, 400],
    "range_ema": [90, 200],
}
DEFAULT_PARAMS = {"bars": 200, "range_ema": 90}


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
    ath = bars_df["high"].rolling(int(p["bars"])).max().shift(1)
    ema = c.ewm(span=int(p["range_ema"]), adjust=False).mean()
    entry = (c > ath).to_numpy()
    exit_ = ((c < ema) & (c.shift(1) >= ema.shift(1))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and entry[i]:
            le[i], pos = True, 1
        elif pos == 1 and exit_[i]:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
