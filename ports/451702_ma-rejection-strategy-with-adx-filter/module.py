"""Rejections of the WMA 50, 1-hour bars: a bar dipping under the WMA 50 and closing over it and over the WMA 10, as the WMA 10 crosses over the WMA 20 with a hand-made ADX over 20, goes long; the mirror goes short; the close crossing back under (over) the WMA 50 closes the long (short); reversing.
Port of FMZ strategy #451702 "MA Rejection Strategy with ADX Filter" (MA Rejection Strategy with ADX Filter).

FMZ source id: 451702

Source
    https://www.fmz.com/strategy/451702 (PineScript v5, FMZ last modified 2024-05-17 10:35:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-164), WMA 10 / 50 / 20; ADX 14 (all WMA-smoothed, by hand), threshold 20
    low < wma50 and close > wma50 and close > wma10 and crossover(wma10, wma20) and adx > 20 -> entry Long;  else crossunder(close, wma50) -> close Long
    high > wma50 and close < wma50 and close < wma10 and crossunder(wma10, wma20) and adx > 20 -> entry Short;  else crossover(close, wma50) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ADX is written out with WMA smoothing as in the source (directional moves, true range, the
      DX and the ADX itself all ta.wma); a 0 / 0 directional sum is na. The long block runs before the
      short block: a long entry with the short's exit reverses and the close then finds the short
      reversed; a long close with a short entry is one reversal. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, WMA rejections with an ADX filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451702_wma50_rejection_wma_adx_filter_reversal"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "slow": [50, 100],
    "adx_min": [20, 25],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 50, "avg": 20, "adx_len": 14, "adx_min": 20}


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


def _wma(x, n):
    """Pine ta.wma: weights 1..n, newest heaviest; na until n values (an na inside stays na)."""
    n = int(n)
    out = pd.Series(0.0, index=x.index)
    for k in range(n):
        out = out + (n - k) * x.shift(k)
    return out / (n * (n + 1) / 2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    fast, slow, avg = _wma(c, p["fast"]), _wma(c, p["slow"]), _wma(c, p["avg"])
    n = int(p["adx_len"])
    dp, dm = h - h.shift(1), lo.shift(1) - lo
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    pdm = dp.where((dp > 0) & (dp > dm), 0.0)       # an na move tests false: 0, as Pine
    mdm = dm.where((dm > 0) & (dm > dp), 0.0)
    trs = _wma(tr, n)
    dip, dim = _wma(pdm, n) / trs * 100, _wma(mdm, n) / trs * 100
    den = dip + dim
    adx = _wma((dip - dim).abs() / den.where(den != 0) * 100, n)
    strong = adx > float(p["adx_min"])
    c1 = c.shift(1)
    long_e = ((lo < slow) & (c > slow) & (c > fast) & (fast > avg) & (fast.shift(1) <= avg.shift(1))
              & strong)
    short_e = ((h > slow) & (c < slow) & (c < fast) & (fast < avg) & (fast.shift(1) >= avg.shift(1))
               & strong)
    long_x = (c < slow) & (c1 >= slow.shift(1))
    short_x = (c > slow) & (c1 <= slow.shift(1))
    return long_e, long_x & ~long_e & ~short_e, short_e, short_x & ~short_e & ~long_e


def portfolio_kwargs(**params):
    return {}
