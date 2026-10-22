"""Close crossings of the SMA 20 and SMA 60, 4-hour bars, long only: from flat, the close crossing over the SMA 20 (or else over the SMA 60) goes long; the long closes only when the close crosses back
under the average that opened it.
Port of FMZ strategy #441003 "Dual Moving Average Breakout Strategy" (Astor SMA20/60).

FMZ source id: 441003

Source
    https://www.fmz.com/strategy/441003 (PineScript v5, FMZ last modified 2024-02-04 16:06:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 127-170), SMA 20 and SMA 60 entries (SMA 10 commented out); qty 1; backtest start date input (unused)
    crossover(close, sma20) -> entry "open long20" qty 1;  crossunder(close, sma20) -> close "open long20";  crossover(close, sma60) -> entry "open long60" qty 1;  crossunder(close, sma60) -> close "open long60"

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default pyramiding allows one entry in a direction, so while either long is open the other
      entry is refused; when both crossings come on the same flat bar the first call (long20) is taken.
      Each close names its own entry, so the long ends only at the crossing back under its own average.
      start_time is never used. Long only. The qty-1 entries are sizing. FREQ = "4h" from the backtest
      header (bars on UTC multiples of 4 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close / SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441003_close_sma20_or_sma60_cross_own_exit_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len_a": [20, 10],
    "len_b": [60, 120],
}
DEFAULT_PARAMS = {"len_a": 20, "len_b": 60}


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
    sa = c.rolling(int(p["len_a"])).mean()
    sb = c.rolling(int(p["len_b"])).mean()
    au = ((c > sa) & (c.shift(1) <= sa.shift(1))).to_numpy()
    ad = ((c < sa) & (c.shift(1) >= sa.shift(1))).to_numpy()
    bu = ((c > sb) & (c.shift(1) <= sb.shift(1))).to_numpy()
    bd = ((c < sb) & (c.shift(1) >= sb.shift(1))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = 0   # 0 flat, 1 the long20 entry, 2 the long60 entry
    for i in range(m):
        if held == 0:
            if au[i] and i + 1 < m:
                le[i], held = True, 1
            elif bu[i] and i + 1 < m:
                le[i], held = True, 2
        elif (held == 1 and ad[i]) or (held == 2 and bd[i]):
            lx[i], held = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
