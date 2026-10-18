"""Fractal-top breakout in a rising fractal average, 1-hour bars, long only: when the average of the last three fractal-top prices is rising and
the previous bar's hl2 is over the latest fractal price, go long; exit three bars after the trend was rising when it is no longer rising.
Port of FMZ strategy #435893 "Fractal Breakout Strategy" (Fractal Breakout Strategy (by ChartArt)).

FMZ source id: 435893

Source
    https://www.fmz.com/strategy/435893 (PineScript v2, FMZ last modified 2023-12-19 15:32:57).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 157-192), fractal top = high[2] over its four neighbours; hl2 price; 3-fractal average; exit after 3 bars
    fractal_top = high[2] > high[3] and high[2] > high[4] and high[2] > high[1] and high[2] > high[0];  fractal_price = valuewhen(fractal_top, hl2, 1);  fractal_average = (fp[1] + fp[2] + fp[3]) / 3;  trend = fa[0] > fa[1]
    breakout = hl2[1] > fractal_price[0];  entry long: trend and breakout;  close long: trend[3] and not trend

Interpretation choices (Pine rules in SURVEY_README.md)
    * A fractal top is confirmed two bars after its high, so it is known at the current bar. The
      fractal price is the hl2 of the CONFIRMING bar (valuewhen of hl2 at the bar where the top is
      detected), the second most recent such value (occurrence 1), as written. The averages use
      the lagged copies fractal_price[1..3]. Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, valuewhen occurrence and lagged copies as written.
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

NAME = "fmz_435893_fractal_top_breakout_long"
FAMILY = "fractal_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n_time": [3, 5],
    "use_longer": [True, False],
}
DEFAULT_PARAMS = {"n_time": 3, "use_longer": True}


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


def _valuewhen(cond, src, occ):
    out = np.full(len(src), np.nan)
    hist = []
    for i in range(len(src)):
        if cond[i]:
            hist.append(src[i])
        if len(hist) > occ:
            out[i] = hist[-1 - occ]
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo = bars_df["high"], bars_df["low"]
    price = (h + lo) / 2
    top = ((h.shift(2) > h.shift(3)) & (h.shift(2) > h.shift(4)) & (h.shift(2) > h.shift(1)) & (h.shift(2) > h)).fillna(False).to_numpy()
    fp = pd.Series(_valuewhen(top, price.to_numpy(dtype=float), 1), index=bars_df.index)
    if p["use_longer"]:
        fa = (fp.shift(1) + fp.shift(2) + fp.shift(3)) / 3
    else:
        fa = (fp.shift(1) + fp.shift(2)) / 2
    trend = (fa > fa.shift(1)).fillna(False)
    breakout = (price.shift(1) > fp).fillna(False)
    n = int(p["n_time"])
    le = (trend & breakout).astype(bool)
    lx = (trend.shift(n, fill_value=False) & ~trend).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
