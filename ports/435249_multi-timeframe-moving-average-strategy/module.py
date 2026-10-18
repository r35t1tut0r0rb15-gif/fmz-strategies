"""Six-average alignment with a bracket, 1-hour bars: SMA 5 > 13 > 21 > EMA 75 > 90 > 200 goes long, the mirror order goes
short (reversing); each trade carries a 200-tick target and a 100-tick stop, re-expressed as ATR multiples.
Port of FMZ strategy #435249 "Multi Timeframe Moving Average Strategy" (my_strategy_name).

FMZ source id: 435249

Source
    https://www.fmz.com/strategy/435249 (PineScript v4, FMZ last modified 2023-12-13 15:34:09).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 150-189), SMA 5 / 13 / 21; EMA 75 / 90 / 200; exit(profit = 200, loss = 100)
    ma1 > ma2 and ma2 > ma3 and ma3 > ema1 and ema1 > ema2 and ema2 > ema3 -> entry long;  the reverse order -> entry short;  exit(profit = 200, loss = 100) on each entry id

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: 200 / 100 ticks (0.1 on BTC: 20 / 10 USD) are far below one 1-hour ATR; the port
      uses tp_stop = 2 x k_atr x ATR / close and sl_stop = k_atr x ATR / close of the signal bar,
      shifted one bar inside stops() (re-based on the fill); k_atr 0.04 is the tick reading, 1.0 a
      volatility-sized bracket. The alignment is a state: while it holds, a new entry is taken on
      the bar after each bracket exit (Pine re-enters), and vbt ignores a same-side signal while in
      a position. The opposite alignment cannot occur on the same bar, but it can arrive while a
      position is open: strategy.entry reverses, REVERSAL INTENDED.
    * Stop module: portfolio_kwargs {} (driver D4). Stops on 1-hour bars: not coarse (60 min or
      less). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick bracket -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the tick bracket quoted in original_sizing.txt.
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

NAME = "fmz_435249_six_average_alignment_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [0.04, 1.0],
    "len3": [21, 34],
}
DEFAULT_PARAMS = {"len1": 5, "len2": 13, "len3": 21, "e1": 75, "e2": 90, "e3": 200, "k_atr": 0.04, "atr_len": 14}


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
    m1 = c.rolling(int(p["len1"])).mean()
    m2 = c.rolling(int(p["len2"])).mean()
    m3 = c.rolling(int(p["len3"])).mean()
    x1 = c.ewm(span=int(p["e1"]), adjust=False).mean()
    x2 = c.ewm(span=int(p["e2"]), adjust=False).mean()
    x3 = c.ewm(span=int(p["e3"]), adjust=False).mean()
    le = ((m1 > m2) & (m2 > m3) & (m3 > x1) & (x1 > x2) & (x2 > x3)).astype(bool)
    se = ((m1 < m2) & (m2 < m3) & (m3 < x1) & (x1 < x2) & (x2 < x3)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    f = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["k_atr"])).shift(1)
    return {"sl_stop": f, "tp_stop": f * 2.0}


def portfolio_kwargs(**params):
    return {}
