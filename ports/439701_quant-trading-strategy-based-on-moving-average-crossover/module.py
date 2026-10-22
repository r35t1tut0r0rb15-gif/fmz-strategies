"""EMA 3 / 5 crossings with a tiny tick bracket, long only, 5-hour bars: the EMA 3 crossing over the EMA 5 goes long; the trade has a 6-tick target and a 5-tick stop, re-expressed as ATR multiples.
Port of FMZ strategy #439701 "Quant Trading Strategy Based on Moving Average Crossover" (Revolut v1.0).

FMZ source id: 439701

Source
    https://www.fmz.com/strategy/439701 (PineScript v3, FMZ last modified 2024-01-23 11:05:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 125-173), ATR 3 (unused); EMA 3 / 5; exit profit 6, loss 5 (ticks); window() true
    entryCondition = crossover(ema(close, 3), ema(close, 5)) -> entry ENTRY (long);  exit("Take Profi Or STOP", profit = 6, loss = 5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the bracket is 6 / 5 ticks from the fill; the port reads it as k_sl x ATR(14) / close
      of the signal bar for the stop and 1.2 times that for the target, shifted one bar inside stops()
      and re-based on the fill (0.00125 is the reading: 0.5 on BTC with 0.1 ticks against a 5-hour ATR
      near 400; 0.5 a wider bracket). Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on
      5-hour bars: mark coarse_bar_stop. No sizing code. FREQ = "5h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick inputs stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_439701_ema3_5_cross_tick_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5h"  # backtest header period: 5h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_sl": [0.00125, 0.5],
}
DEFAULT_PARAMS = {"k_sl": 0.00125, "tp_ratio": 1.2, "atr_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    c = bars_df["close"]
    a, b = c.ewm(span=3, adjust=False).mean(), c.ewm(span=5, adjust=False).mean()
    up = (a > b) & (a.shift(1) <= b.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = float(p["k_sl"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": sl.shift(1), "tp_stop": (float(p["tp_ratio"]) * sl).shift(1)}


def portfolio_kwargs(**params):
    return {}
