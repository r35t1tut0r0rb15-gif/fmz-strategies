"""HPotter smoothed RSI v2: an RSI-like ratio of up- and down-moves of a 1-2-2-1 smoothed close over
10 bars; above 0.8 goes long, below 0.2 goes short (always in the market after the first signal).
Port of FMZ strategy #427467 "Smoothed RSI Backtesting Strategy V2".

FMZ source id: 427467

Source
    https://www.fmz.com/strategy/427467 (PineScript v2, FMZ last modified 2023-09-21 15:02:06).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 139-157), length 10, bands 0.8 / 0.2, reverse off
    x = (close + 2 close[1] + 2 close[2] + close[3]) / 6
    cu = sum(max(x - x[1], 0), 10); cd = sum(max(x[1] - x, 0), 10); r = cu / (cu + cd) (0 when both 0)
    pos = r > 0.8 ? 1 : r < 0.2 ? -1 : pos[1] -> entries on pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written, a high ratio buys and a low one sells (trend reading).
    * strategy.entry reverses: REVERSAL INTENDED; "Trade reverse" is off.
    * FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a ratio of price moves.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: DG427467 (2 members, with #427880, Jaccard 0.800); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427467_hpotter_smoothed_rsi_v2"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20, 5],
    "top_band": [0.8, 0.7],
}
DEFAULT_PARAMS = {"length": 10, "top_band": 0.8}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    c = bars_df["close"]
    x = (c + 2 * c.shift(1) + 2 * c.shift(2) + c.shift(3)) / 6
    dx = x.diff()
    cu = pd.Series(np.where(dx > 0, dx, 0.0), index=c.index).where(dx.notna()).rolling(n).sum()
    cd = pd.Series(np.where(dx < 0, -dx, 0.0), index=c.index).where(dx.notna()).rolling(n).sum()
    tot = cu + cd
    r = np.where(tot.to_numpy() != 0, (cu / tot.where(tot != 0)).to_numpy(), 0.0)
    r[tot.isna().to_numpy()] = np.nan
    top, low = float(p["top_band"]), 1.0 - float(p["top_band"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if r[i] > top:
            pos = 1
        elif r[i] < low:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
