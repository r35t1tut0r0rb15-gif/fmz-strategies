"""EMA 4 crossings of an SMA 50 corridor, 1-hour bars: the EMA crossing back under SMA + 1.2 sd(30) goes short, crossing back over SMA - 1.2 sd goes long; a high reaching SMA + 1.6 sd closes a long, a low
reaching SMA - 1.6 sd closes a short; reversing.
Port of FMZ strategy #449506 "Quantitative Trading Strategy Based on Moving Averages and Bollinger Bands" (Marina Parfenova School Project Bot).

FMZ source id: 449506

Source
    https://www.fmz.com/strategy/449506 (PineScript v5, FMZ last modified 2024-04-26 11:45:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 110-184), SMA 50 (hand-written); EMA 4 (hand-written); sd 30; open corridor x 1.2, close corridor x 1.6
    ema[1] >= sma + 1.2 sd and ema < it -> entry short;  ema[1] <= sma - 1.2 sd and ema > it -> entry long;  high >= sma + 1.6 sd -> close long;  low <= sma - 1.6 sd -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The hand-written SMA and EMA are the usual ones (the EMA seeds with the first price). The closes
      are bar-close tests of the high / low, filled at the next open, and act only on a position held
      into the bar and not reversed by that bar's entry. Pine's stdev is the population deviation.
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings of an SMA corridor with wider-corridor exits.
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

NAME = "fmz_449506_ema4_sma50_corridor_cross_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "k_open": [1.2, 1.0],
    "k_close": [1.6, 2.0],
}
DEFAULT_PARAMS = {"k_open": 1.2, "k_close": 1.6, "n_slow": 50, "n_fast": 4, "n_dev": 30}


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
    sma = c.rolling(int(p["n_slow"])).mean()
    sd = c.rolling(int(p["n_dev"])).std(ddof=0)
    os_line = sma + float(p["k_open"]) * sd
    ol_line = sma - float(p["k_open"]) * sd
    cs_line = (sma + float(p["k_close"]) * sd).to_numpy()
    cl_line = (sma - float(p["k_close"]) * sd).to_numpy()
    e = c.ewm(span=int(p["n_fast"]), adjust=False).mean()
    e1 = e.shift(1)
    with np.errstate(invalid="ignore"):
        sc = ((e1 >= os_line.shift(1)) & (e < os_line)).to_numpy()
        lc = ((e1 <= ol_line.shift(1)) & (e > ol_line)).to_numpy()
        xl = h.to_numpy(dtype=float) >= cs_line
        xs = lo.to_numpy(dtype=float) <= cl_line
    m = len(sc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if sc[i] and new != -1:
            se[i], new = True, -1
        if lc[i] and new != 1:
            le[i], se[i], new = True, False, 1
        if xl[i] and pos == 1 and new == 1:          # a close acts only on a held, non-reversed long
            lx[i], new = True, 0
        if xs[i] and pos == -1 and new == -1:
            sx[i], new = True, 0
        pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
