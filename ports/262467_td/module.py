"""TD-sequential style count: fade a 9/13/22-bar run (close vs close 4 bars back), take
profit as soon as the count turns 2 bars the other way.
Port of FMZ strategy #262467 "TD狄马克序列" (TD DeMark sequence).

Source
    https://www.fmz.com/strategy/262467 (Python, author "btccccrazy", FMZ last modified
    2021-03-16 11:18:47). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 28-88)
    records = GetRecords(PERIOD_H1); over the last 40 bars:
      i = consecutive count of close > close[4 bars back] (reset otherwise)
      j = -(consecutive count of close < close[4 bars back])
    TDindex = i if i > 0 else j
    TDindex in {9, 13, 22}    -> sell 1 (open short)
    TDindex in {-9, -13, -22} -> buy 1 (open long)
    long held and TDindex >= 2 -> close 1 long;  short held and TDindex <= -2 -> close 1 short

Interpretation choices
    * The bot polls every 15 min and reads the forming hourly bar as the last record; the port
      evaluates on completed bar t (last record -> t). Counting inside a 40-bar window equals the
      run length capped at 40; the trigger values are all below 40, so the cap changes nothing.
    * On FMZ a "sell" while long opens a hedged short leg and the same pass closes the long
      (TDindex >= 2), so the net effect is a reversal: REVERSAL INTENDED (portfolio_kwargs {};
      the engine's default opposite-entry reversal applies). Repeated same-side sells on later
      polls are adds (sizing).
    * FREQ = "1h" (code requests PERIOD_H1; the header's 15m is the backtest's base period).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_262467_td_count_fade"
FAMILY = "td_sequential"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # code requests PERIOD_H1
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [3, 4, 5],
    "exit_count": [1, 2, 3],
}
DEFAULT_PARAMS = {"lookback": 4, "exit_count": 2}
SETUPS = (9, 13, 22)


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
    k = int(p["lookback"])
    c = bars_df["close"].to_numpy(dtype=float)
    m = len(c)
    td = np.zeros(m, dtype=int)
    up = dn = 0
    for x in range(k, m):
        up = up + 1 if c[x] > c[x - k] else 0
        dn = dn - 1 if c[x] < c[x - k] else 0
        td[x] = min(up, 40) if up > 0 else max(dn, -40)

    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        if td[i] in SETUPS:
            if pos != -1:
                se[i], pos = True, -1          # from long this reverses
        elif -td[i] in SETUPS:
            if pos != 1:
                le[i], pos = True, 1
        elif pos == 1 and td[i] >= p["exit_count"]:
            lx[i], pos = True, 0
        elif pos == -1 and td[i] <= -p["exit_count"]:
            sx[i], pos = True, 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
