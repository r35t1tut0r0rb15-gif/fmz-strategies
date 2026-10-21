"""SMA 10 / 30 crossings with a close_all on the cross down, 5-minute bars: the SMA 10 crossing over the SMA 30 goes long (from flat or short); the cross under flattens a long, and opens a short only from flat.
Port of FMZ strategy #438010 "Crude Oil Moving Average Crossover Strategy" (Crude Oil Moving Average Crossover).

FMZ source id: 438010

Source
    https://www.fmz.com/strategy/438010 (PineScript v5, FMZ last modified 2024-01-08 10:25:00).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 162-186), SMA 10 / 30
    crossover(fast, slow) -> entry Buy;  crossunder(fast, slow) -> entry Sell;  crossover(slow, fast) (the same cross under) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close_all is written after the opposite entry on the same bar; it acts on the position held
      at the bar close and the bar ends flat (the convention used for close_all after an entry in these
      ports, as #430380), so a cross under flattens a long and opens a short only from flat. A cross
      over reverses a short. REVERSAL INTENDED. No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crossings.
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

NAME = "fmz_438010_sma10_30_cross_close_all"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "slow": [30, 60],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if up[i] and pos != 1 and i + 1 < m:
            le[i], pos = True, 1
        elif dn[i]:
            if pos == 1:
                lx[i], pos = True, 0
            elif pos == 0 and i + 1 < m:
                se[i], pos = True, -1
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
