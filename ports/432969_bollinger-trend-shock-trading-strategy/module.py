"""Bollinger dips in the trend, 1-hour bars: with the whole EMA-20 / 2.3-sd band above the SMA 200 a close crossing up
through the lower band goes long, and a high crossing the upper band closes it; with the whole band below the SMA 200 a
close crossing up through the upper band goes short, closed by a close under the basis or above the SMA 230.
Port of FMZ strategy #432969 "Bollinger Trend Shock Trading Strategy" (布林趋势震荡单 (Bollinger trend shock)).

FMZ source id: 432969

Source
    https://www.fmz.com/strategy/432969 (PineScript v5, FMZ last modified 2023-11-23 10:57:10).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 132-163), EMA basis 20, stdev 2.3, trend SMA 200, short exit SMA 230
    longT = upper > sma200 and basis > sma200 and lower >= sma200;  shortT = upper < sma200 and basis < sma200 and lower <= sma200
    longT and crossover(close, lower) -> entry long;  crossover(high, upper) -> close long
    shortT and crossover(close, upper) -> entry short;  crossunder(close, basis) or crossover(close, sma(close, 230)) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short entry is a close crossing UP through the upper band while the band is below the SMA
      200, as written. Pine's stdev is the population stdev.
    * Each bar: the exits act on the position held at the start of the bar, then an entry wins (a
      long entry while short reverses it, as strategy.entry does).
    * REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band crosses relative to moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() fixed quantity 1 stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG432969 (2 members, best partner #434569, Jaccard 0.849); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432969_bb_trend_dip"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "boll_len": [20, 40],
    "boll_mult": [2.3, 1.5],
}
DEFAULT_PARAMS = {"boll_len": 20, "boll_mult": 2.3, "trend_len": 200, "exit_len": 230}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _xover(a, b):
    return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, c = bars_df["high"], bars_df["close"]
    n = int(p["boll_len"])
    basis = c.ewm(span=n, adjust=False).mean()
    dev = float(p["boll_mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    sma = c.rolling(int(p["trend_len"])).mean()
    sma2 = c.rolling(int(p["exit_len"])).mean()
    long_t = ((up > sma) & (basis > sma) & (dn >= sma)).to_numpy()
    short_t = ((up < sma) & (basis < sma) & (dn <= sma)).to_numpy()
    le = long_t & _xover(c, dn)
    se = short_t & _xover(c, up)
    lx = _xover(h, up)
    sx = _xover(basis, c) | _xover(c, sma2)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 1 and lx[i]:
            pos = 0
        elif pos == -1 and sx[i]:
            pos = 0
        if le[i]:
            pos = 1
        elif se[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
