"""BB / Keltner squeeze release, 30-minute bars: a squeeze is the Keltner upper band (EMA 20 + 1.5 EMA
of true range) above the Bollinger upper band (SMA 20 + 2 stdev). When a squeeze ends with the close
above the SMA go long, below it go short; close as soon as the state changes again (a new squeeze or
the close crossing the SMA).
Port of FMZ strategy #427810 "BB Keltner Squeeze Trading Strategy".

FMZ source id: 427810

Source
    https://www.fmz.com/strategy/427810 (PineScript v4, FMZ last modified 2023-09-25 17:38:08).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 199-260), length 20, BB 2, Keltner 1.5 (true range)
    squeeze = Kupper > BBupper; midc = squeeze ? 0 : close > basis ? 1 : 2
    direction = midc[1]
    direction == 0: midc == 1 -> entry long; midc == 2 -> entry short
    direction != midc (and not 0) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * `direction` is not var: each bar it is midc[1], so the rule reads off the last two states.
    * Opposite entries cannot occur: entries only follow a squeeze bar, and any open position was
      closed when the squeeze began.
    * The oscillator, diff and the year inputs are drawn / unused.
    * tr is na on the first bar (Pine's tr without na handling).
    * FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bands in standard deviations and true-range multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: initial capital only (one contract) stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427810_bb_keltner_squeeze_release"
FAMILY = "volatility_squeeze"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "bb_mult": [2.0, 1.5],
    "k_mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "bb_mult": 2.0, "k_mult": 1.5}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    bb_up = basis + p["bb_mult"] * c.rolling(n).std(ddof=0)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    k_up = c.ewm(span=n, adjust=False).mean() + tr.ewm(span=n, adjust=False, ignore_na=True).mean() * p["k_mult"]
    squeeze = (k_up > bb_up).to_numpy()
    above = (c > basis).to_numpy()
    midc = np.where(squeeze, 0, np.where(above, 1, 2))
    m = len(midc)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(1, m):
        d = midc[i - 1]
        if d == 0:
            if midc[i] == 1:
                pos = 1
            elif midc[i] == 2:
                pos = -1
        elif d != midc[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
