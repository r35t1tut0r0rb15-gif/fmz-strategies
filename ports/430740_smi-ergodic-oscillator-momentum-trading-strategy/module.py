"""SMI ergodic (TSI form, HPotter), 1-hour bars: the EMA 3 of the double-smoothed momentum ratio (4 / 8) under -0.5 holds a
short, over 0.5 holds a long.
Port of FMZ strategy #430740 "SMI Ergodic Oscillator Momentum Trading Strategy" (SMI Ergodic Oscillator).

FMZ source id: 430740

Source
    https://www.fmz.com/strategy/430740 (PineScript v2, FMZ last modified 2023-11-01 11:19:18).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 197-240), fast 4, slow 8, smoothing 3, bands 0.5 / -0.5
    smi = ema(ema(close - close[1], 4), 8) / ema(ema(|close - close[1]|, 4), 8); sig = ema(smi, 3)
    sig < -0.5 -> -1 (entry short);  sig > 0.5 -> 1 (entry long);  else pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Trade reverse" defaults to false and is fixed. strategy.entry reverses: REVERSAL INTENDED.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a bounded momentum ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG430740 (2 members, best partner #432119, Jaccard 0.915); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430740_smi_ergodic_bands"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow_period": [8, 20],
    "band": [0.5, 0.3],
}
DEFAULT_PARAMS = {"fast_period": 4, "slow_period": 8, "smth_len": 3, "band": 0.5}


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
    c = bars_df["close"]
    d = c.diff()
    f, s = int(p["fast_period"]), int(p["slow_period"])
    num = d.ewm(span=f, adjust=False).mean().ewm(span=s, adjust=False).mean()
    den = d.abs().ewm(span=f, adjust=False).mean().ewm(span=s, adjust=False).mean()
    sig = (num / den.replace(0.0, np.nan)).ewm(span=int(p["smth_len"]), adjust=False).mean().to_numpy()
    b = float(p["band"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if sig[i] < -b:
            pos = -1
        elif sig[i] > b:
            pos = 1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
