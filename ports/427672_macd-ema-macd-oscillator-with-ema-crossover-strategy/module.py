"""MACD histogram flip with an EMA filter, long only: go long when the histogram turns positive while the
close is above a rising EMA 9 of hl2 and above the previous close; close the long on the mirror
(histogram turns negative under a falling EMA with a lower close).
Port of FMZ strategy #427672 "MACD Oscillator with EMA Crossover Strategy" (SoftKill21).

FMZ source id: 427672

Source
    https://www.fmz.com/strategy/427672 (PineScript v4, FMZ last modified 2023-09-23 15:24:12).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 229-321), EMA 9 of hl2, MACD 12/26/9 of hl2 (EMA)
    long = close > out and close > close[1] and out > out[1] and hist > 0 and hist[1] < 0
    short = close < out and close < close[1] and out < out[1] and hist < 0 and hist[1] > 0
    longCondition = long and not longOpened (flag set); exitLong = longOpened[1] and short (flag cleared)
    longEntry true: entry long on longCondition, close on exitLong; shortEntry false (off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Heikin Ashi is off by default (the chart's own candles); the short switch is off: Long only.
    * The "opened" flag follows the signals, not the fills (as written); with one long at a time
      it equals the position.
    * time_cond is true (the date inputs are unused).
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending"
      (rule 1). precompute builds the bars with the house bar_sizes.build_bars(raw_1m_df,
      params["bar_size"]); the driver supplies bar_size (never in GRID / DEFAULT_PARAMS).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (no exchange in the source).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_427672_macd_hist_flip_ema_long"
FAMILY = "macd_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # source declares no bar size; set by the project before running
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [9, 21],
    "signal_length": [9, 5],
}
DEFAULT_PARAMS = {"len": 9, "fast_length": 12, "slow_length": 26, "signal_length": 9}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    src = (bars_df["high"] + bars_df["low"]) / 2
    out = src.ewm(span=int(p["len"]), adjust=False).mean()
    macd = src.ewm(span=int(p["fast_length"]), adjust=False).mean() - \
        src.ewm(span=int(p["slow_length"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["signal_length"]), adjust=False).mean()
    long_s = ((c > out) & (c > c.shift(1)) & (out > out.shift(1)) & (hist > 0) & (hist.shift(1) < 0)).to_numpy()
    short_s = ((c < out) & (c < c.shift(1)) & (out < out.shift(1)) & (hist < 0) & (hist.shift(1) > 0)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    opened = False
    for i in range(m):
        prev = opened
        if long_s[i] and not opened:
            opened = True
            le[i] = True
        if prev and short_s[i]:
            opened = False
            lx[i] = True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
