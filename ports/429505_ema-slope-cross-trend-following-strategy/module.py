"""EMA slope comparison, 1-minute bars: the smoothed slope of EMA 130 above that of EMA 400 with the close above the
EMA 200 holds a long, the mirror holds a short; a slope cross against the position closes it.
Port of FMZ strategy #429505 "EMA Slope Cross Trend Following Strategy".

FMZ source id: 429505

Source
    https://www.fmz.com/strategy/429505 (PineScript v4, FMZ last modified 2023-10-17 17:02:30).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 206-309), EMA 130 / 400, slope smoothing EMA 3, trend filter EMA 200, volatility filter off
    e1 = ema((m1 - m1[1]) / m1, 3); e2 = the same for m2
    exit: crossover(e1, e2) closes a short; crossunder(e1, e2) closes a long
    entry: e1 > e2 and close > ema200 -> entry long; e1 < e2 and close < ema200 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source MA type, smoothing type and trend-filter type default to EMA; the volatility filter is
      off. The strategy() line is commented out. The dates are unused.
    * Closes are evaluated before entries; an entry on the other side reverses: REVERSAL INTENDED.
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, slope fractions and a moving-average side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() stored.
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

NAME = "fmz_429505_ema_slope_compare"
FAMILY = "slope_momentum"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [130, 50],
    "len2": [400, 200],
}
DEFAULT_PARAMS = {"len1": 130, "len2": 400, "smooth": 3, "trend": 200}


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
    e = lambda x, n: x.ewm(span=int(n), adjust=False).mean()  # noqa: E731
    m1, m2 = e(c, p["len1"]), e(c, p["len2"])
    e1 = e((m1 - m1.shift(1)) / m1, p["smooth"])
    e2 = e((m2 - m2.shift(1)) / m2, p["smooth"])
    t = e(c, p["trend"])
    el = ((e1 > e2) & (c > t)).to_numpy()
    es = ((e1 < e2) & (c < t)).to_numpy()
    xl = ((e1 < e2) & (e1.shift(1) >= e2.shift(1))).to_numpy()
    xs = ((e1 > e2) & (e1.shift(1) <= e2.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == -1 and xs[i]:
            pos = 0
        if pos == 1 and xl[i]:
            pos = 0
        if el[i]:
            pos = 1
        if es[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
