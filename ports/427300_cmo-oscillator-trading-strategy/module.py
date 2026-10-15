"""CMOabsav: the absolute average of three Chande momentum oscillators (5, 10, 20); above 58 goes
long, below 5 goes short (always in the market after the first signal).
Port of FMZ strategy #427300 "CMO Oscillator Trading Strategy".

FMZ source id: 427300

Source
    https://www.fmz.com/strategy/427300 (PineScript v2, FMZ last modified 2023-09-19 21:16:26).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 154-180), lengths 5 / 10 / 20, TopBand 58, LowBand 5
    nRes = abs(100 (sum(mom, 5) / sum(|mom|, 5) + ... 10 ... + ... 20 ...) / 3)
    pos = nRes > 58 ? 1 : nRes < 5 ? -1 : pos[1] -> entries on pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written: a strong move in EITHER direction (|CMO| high) buys and a quiet market sells.
    * A window with no movement (sum of |mom| = 0) gives na (no change of state).
    * strategy.entry reverses: REVERSAL INTENDED; "Trade reverse" is off.
    * FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a ratio of price changes (dimensionless).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427300_cmo_abs_average"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "top_band": [58, 40, 70],
    "low_band": [5, 15],
}
DEFAULT_PARAMS = {"length1": 5, "length2": 10, "length3": 20, "top_band": 58, "low_band": 5}


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
    mom = c.diff()
    total = 0
    for k in ("length1", "length2", "length3"):
        n = int(p[k])
        den = mom.abs().rolling(n).sum()
        total = total + mom.rolling(n).sum() / den.where(den != 0)
    res = (100 * total / 3).abs().to_numpy()
    m = len(res)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if res[i] > p["top_band"]:
            pos = 1
        elif res[i] < p["low_band"]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
