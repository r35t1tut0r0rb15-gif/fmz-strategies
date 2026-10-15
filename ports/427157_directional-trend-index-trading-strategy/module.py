"""Directional Trend Index (DTI), contrarian: the triple-smoothed balance of up-moves of highs and
down-moves of lows, as a percentage of its absolute value; above +45 goes short, below -45 goes
long (always in the market after the first signal).
Port of FMZ strategy #427157 "Directional Trend Index Trading Strategy".

FMZ source id: 427157

Source
    https://www.fmz.com/strategy/427157 (PineScript v2, FMZ last modified 2023-09-18 17:07:55).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 135-159), r 14, s 10, u 5, OS 45, OB -45, reverse off
    xPrice = max(high - high[1], 0) - max(low[1] - low, 0)
    DTI = 100 ema(ema(ema(xPrice, r), s), u) / ema(ema(ema(abs(xPrice), r), s), u)
    pos = DTI > 45 ? -1 : DTI < -45 ? 1 : pos[1] -> entries on pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written: a high DTI (inputs named OS) sells and a low one (OB) buys.
    * iff(high - high[1] > 0, ...) is 0 on the first bar (na > 0 is false). DTI is 0 where the
      denominator is 0.
    * strategy.entry reverses: REVERSAL INTENDED; "Trade reverse" is off.
    * FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a ratio of smoothed price moves (dimensionless).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427157_directional_trend_index"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "r": [14, 25],
    "level": [45, 30],
    "s": [10, 5],
}
DEFAULT_PARAMS = {"r": 14, "s": 10, "u": 5, "level": 45}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _ema3(x, r, s, u):
    return x.ewm(span=r, adjust=False).mean().ewm(span=s, adjust=False).mean().ewm(span=u, adjust=False).mean()


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
    dh = bars_df["high"].diff()
    dl = bars_df["low"].diff()
    hmu = pd.Series(np.where(dh > 0, dh, 0.0), index=bars_df.index)
    lmd = pd.Series(np.where(dl < 0, -dl, 0.0), index=bars_df.index)
    x = hmu - lmd
    r, s, u = int(p["r"]), int(p["s"]), int(p["u"])
    num = 100 * _ema3(x, r, s, u)
    den = _ema3(x.abs(), r, s, u)
    with np.errstate(divide="ignore", invalid="ignore"):
        dti = np.where(den.to_numpy() != 0, num.to_numpy() / den.to_numpy(), 0.0)
    lvl = float(p["level"])
    m = len(dti)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if dti[i] > lvl:
            pos = -1
        elif dti[i] < -lvl:
            pos = 1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
