"""Z-score of the close's distance from the EMA 21, 4-hour bars: the z-score crossing over 0.5 goes long, under -0.5 short; a long closes when it falls back under 0.5 or crosses over 3, a short when it
rises back over -0.5 or crosses under -3; reversing.
Port of FMZ strategy #442264 "All About Momentum Trading Strategy with Stop Loss for Gold" (GC Momentum Strategy with Stoploss and Limits).

FMZ source id: 442264

Source
    https://www.fmz.com/strategy/442264 (PineScript v5, FMZ last modified 2024-02-20 16:27:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 142-199), EMA 21; z = (close - ema) / stdev(close - ema, 21); levels 0.5 / 3
    crossover(z, 0.5) -> entry Long;  crossunder(z, -0.5) -> entry Short;  crossunder(z, 0.5) or crossover(z, 3) -> close Long;  crossover(z, -0.5) or crossunder(z, -3) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's stdev is the population deviation. A close acts only on the held position; a close written
      after a reversing entry leaves the reversal standing (as #438020). REVERSAL INTENDED. No sizing code.
      FREQ = "4h" from the backtest header (bars on UTC multiples of 4 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, z-score crossings.
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

NAME = "fmz_442264_ema21_zscore_cross_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [21, 50],
    "entry_z": [0.5, 1.0],
}
DEFAULT_PARAMS = {"ema_length": 21, "entry_z": 0.5, "stop_z": 3.0}


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
    n = int(p["ema_length"])
    dev = c - c.ewm(span=n, adjust=False).mean()
    sd = dev.rolling(n).std(ddof=0)
    z = dev / sd.where(sd != 0)
    ez, sz = float(p["entry_z"]), float(p["stop_z"])
    z1 = z.shift(1)

    def over(lv):
        return ((z > lv) & (z1 <= lv)).to_numpy()

    def under(lv):
        return ((z < lv) & (z1 >= lv)).to_numpy()

    el, es = over(ez), under(-ez)
    xl = under(ez) | over(sz)
    xs = over(-ez) | under(-sz)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if el[i] and new != 1:
            new = 1
        if es[i] and new != -1:
            new = -1
        if xl[i] and held == 1 and new == 1:
            new = 0
        if xs[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
