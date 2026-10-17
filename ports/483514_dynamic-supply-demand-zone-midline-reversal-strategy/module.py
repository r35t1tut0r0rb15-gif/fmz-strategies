"""Engulfing-style candle reversals between SMA 20 and the 50-bar range midpoint, with the stop at the range extreme
behind and the target at the range extreme ahead, 1-minute bars: a green bar that opens below the prior red bar's close,
with the close above SMA 20 but below the midpoint of the 50-bar high / low, goes long (target the 50-bar high, stop
the 50-bar low); the mirror goes short.
Port of FMZ strategy #483514 "动态供需区间中线反转策略-Dynamic-Supply-Demand-Zone-Midline-Reversal-Strategy" (Midline Rejection Entry with TP/SL at Supply/Demand).

FMZ source id: 483514

Source
    https://www.fmz.com/strategy/483514 (PineScript v6, FMZ last modified 2025-02-24 16:00:34).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 133-188), swing length 50, SMA 20
    long = close > sma20 and close < midpoint and close > open and open < close[1] and close[1] < open[1]
    short = close < sma20 and close > midpoint and close < open and open > close[1] and close[1] > open[1]
    on a signal: close_all, then entry; exits at the stored zones: long limit = supply, stop = demand (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The zones are stored at the signal bar: the target and stop distances are fractions of the signal bar's close
      (long: (highest high 50 - close) / close and (close - lowest low 50) / close; short mirrored), picked by the
      signal's side, shifted one bar inside stops() and re-based on the fill (house rule). Both are always positive
      (the candle conditions keep the close inside the range).
    * close_all + the opposite entry is a reversal (REVERSAL INTENDED). A same-side signal while held re-stores the
      zones: mark trailing_stop_pending; the port keeps the entry's bracket.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, rolling range extremes, a moving average and candle colours (no fixed price levels).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483514_midline_candle_reversal_range_bracket"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [50, 100],
    "midline_len": [20, 50],
}
DEFAULT_PARAMS = {"length": 50, "midline_len": 20}


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


def _levels(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    supply, demand = h.rolling(n).max(), lo.rolling(n).min()
    mid = (supply + demand) / 2
    trend = c.rolling(int(p["midline_len"])).mean()
    long_e = ((c > trend) & (c < mid) & (c > o) & (o < c.shift(1)) & (c.shift(1) < o.shift(1))).astype(bool)
    short_e = ((c < trend) & (c > mid) & (c < o) & (o > c.shift(1)) & (c.shift(1) > o.shift(1))).astype(bool)
    return long_e, short_e, supply, demand, c


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _, _, _ = _levels(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, _, supply, demand, c = _levels(bars_df, p)
    up, dn = (supply - c) / c, (c - demand) / c
    sl = dn.where(long_e, up)
    tp = up.where(long_e, dn)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
