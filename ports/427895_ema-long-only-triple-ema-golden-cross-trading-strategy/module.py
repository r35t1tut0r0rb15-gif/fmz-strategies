"""EMA golden cross, long only, 5-minute bars: EMA 8 crossing above EMA 50 goes long; the close crossing
under the EMA 50 "profit level" closes it.
Port of FMZ strategy #427895 "Long Only Triple EMA Golden Cross Trading Strategy".

FMZ source id: 427895

Source
    https://www.fmz.com/strategy/427895 (PineScript v2, FMZ last modified 2023-09-26 16:23:53).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 158-189), EMAs 8 / 50 / 200, profit level EMA 50
    bullish = crossover(ema8, ema50) (and ema8 > ema200 when "Long only above EMA200", default off)
    bearish = crossunder(close, ema_profit 50)
    bullish -> entry long; bearish -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The EMA 200 switch defaults off (not searched). An entry and a close on one bar: the close
      acts only on an open position.
    * Long only. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427895_ema_golden_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 13],
    "slow": [50, 30],
}
DEFAULT_PARAMS = {"fast": 8, "slow": 50, "profit": 50}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    pl = c.ewm(span=int(p["profit"]), adjust=False).mean()
    bull = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    bear = ((c < pl) & (c.shift(1) >= pl.shift(1))).to_numpy()
    m = len(bull)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if bull[i]:
            pos = 1
        if start == 1 and bear[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
