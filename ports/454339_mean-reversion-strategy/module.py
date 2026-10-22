"""SMA 20 +- 1.5 SD band re-entries, 4-hour bars: the close crossing back over the lower band goes long, back under the upper band goes short; the close crossing under (over) the SMA closes the long (short); reversing.
Port of FMZ strategy #454339 "Mean Reversion Strategy" (Mean Regression Strategy).

FMZ source id: 454339

Source
    https://www.fmz.com/strategy/454339 (PineScript v5, FMZ last modified 2024-06-17 14:57:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-137), SMA 20; 1.5 SD bands
    crossover(close, lower) -> entry Long;  crossunder(close, upper) -> entry Short;  crossunder(close, sma) -> close Long;  crossover(close, sma) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are called before the closes; an opposite entry reverses and the close then finds
      the trade reversed; a close acts only on the trade held into the bar. REVERSAL INTENDED. No
      sizing code. FREQ = "4h" from the backtest header (UTC-aligned 4-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band re-entries with basis exits.
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

NAME = "fmz_454339_sma20_sd_band_reentry_basis_exit_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 1.5}


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
    n = int(p["length"])
    ma = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, lo = ma + dev, ma - dev
    c1 = c.shift(1)
    el = ((c > lo) & (c1 <= lo.shift(1))).to_numpy()
    es = ((c < up) & (c1 >= up.shift(1))).to_numpy()
    xl = ((c < ma) & (c1 >= ma.shift(1))).to_numpy()
    xs = ((c > ma) & (c1 <= ma.shift(1))).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if el[i] and cur != 1:
            cur = 1
        if es[i] and cur != -1:
            cur = -1
        if xl[i] and pos == 1 and cur == 1:
            cur = 0
        if xs[i] and pos == -1 and cur == -1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
