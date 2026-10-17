"""Super Guppy slow-ribbon transitions (early signals), 1-minute bars: the fifteen slow EMAs (24 to 66) turning from mixed
to stacked up, or from stacked down to mixed, goes long; turning from stacked up to mixed, or from mixed to stacked down,
goes short; always in once started.
Port of FMZ strategy #432778 "Super Guppy Moving Average Trading Strategy" (Super Guppy Strategy).

FMZ source id: 432778

Source
    https://www.fmz.com/strategy/432778 (PineScript v4, FMZ last modified 2023-11-21 14:05:40).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 170-322), slow EMAs 24 / 27 / ... / 66, early signals on, shorts on
    colour = slow EMAs stacked up ? lime : stacked down ? red : gray
    long = not isLong and (lime after gray or gray after red);  short = not isShort and (gray after lime or red after gray)
    long -> entry long (closes the short);  short -> close long and entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * With early signals on, only the second order block acts; the last close line needs early
      signals off and is inert. The fast ribbon only colours the plot. isLong / isShort make each
      side fire once per run, i.e. on a change of side. The time bounds (100,000 days back from now)
      are always true.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA ribbon order.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
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

NAME = "fmz_432778_super_guppy_slow_ribbon"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "step": [3, 2],
    "first": [24, 12],
}
DEFAULT_PARAMS = {"first": 24, "step": 3, "count": 15}


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
    lens = [int(p["first"]) + int(p["step"]) * j for j in range(int(p["count"]))]
    em = np.column_stack([c.ewm(span=n, adjust=False).mean().to_numpy() for n in lens])
    up = np.all(em[:, :-1] > em[:, 1:], axis=1)
    dn = np.all(em[:, :-1] < em[:, 1:], axis=1)
    col = np.where(up, 1, np.where(dn, -1, 0))              # 1 lime, -1 red, 0 gray
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    is_l = is_s = False
    pos = 0
    for i in range(1, m):
        a, b = col[i], col[i - 1]
        lg = (not is_l) and ((a == 1 and b == 0) or (a == 0 and b == -1))
        sh = (not is_s) and ((a == 0 and b == 1) or (a == -1 and b == 0))
        if lg:
            is_l, is_s = True, False
            pos = 1
        if sh:
            is_l, is_s = False, True
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
