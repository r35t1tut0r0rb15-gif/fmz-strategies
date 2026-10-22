"""Close crossings of the 0.65 retracement of the 38-bar range on the side of the SMA 181, 3-hour bars: the cross up above the SMA goes long, the cross down below it goes short; reversing. The 1.8 ATR bracket is re-sent every bar from the latest close while a position is held and is not ported (pending).
Port of FMZ strategy #476243 "Enhanced Fibonacci Trend Following and Risk Management Strategy" (Refined Fibonacci Strategy - Enhanced Risk Management).

FMZ source id: 476243

Source
    https://www.fmz.com/strategy/476243 (PineScript v5, FMZ last modified 2024-12-27 14:10:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-144), Fibonacci lookback 38; SMA 181; ATR 12 x 1.8 stop and target from the current close
    change(highest(high, 38)) -> high_level := highest;  change(lowest(low, 38)) -> low_level := lowest;  fib = high_level - 0.65 (high_level - low_level)
    close > fib and close[1] <= fib and close > sma181 -> entry Buy;  close < fib and close[1] >= fib and close < sma181 -> entry Sell;  in a position every bar: exit(stop = close -/+ 1.8 atr, limit = close +/- 1.8 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * high_level (low_level) is set whenever the 38-bar high (low) changes, so after its first change it
      always equals the current 38-bar high (low); before that it is na. The cross test compares the
      previous close with the CURRENT level, as written. The bracket is sent on every bar while a position
      is held, from that bar's close and ATR, so its levels move after entry: stops() cannot express a
      level re-set every bar, so it is described here and kept pending (as #438034, mark
      trailing_stop_pending). REVERSAL INTENDED. No sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar bracket described (pending).
    2 generic: PASS, range-retracement crossings with an SMA trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the ATR bracket inputs stored.
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

NAME = "fmz_476243_fib065_range_cross_sma181_side_reversal"
FAMILY = "channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [38, 20],
    "sma_length": [181, 100],
}
DEFAULT_PARAMS = {"lookback": 38, "sma_length": 181}


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


def _set_on_change(x):
    """var level := x whenever ta.change(x) is non-zero: na until the first change, then x."""
    d = x.diff()
    started = ((d != 0) & d.notna()).cummax()
    return x.where(started)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["lookback"])
    hl = _set_on_change(h.rolling(n).max())
    ll = _set_on_change(lo.rolling(n).min())
    fib = hl - (hl - ll) * 0.65
    sma = c.rolling(int(p["sma_length"])).mean()
    le = (c > fib) & (c.shift(1) <= fib) & (c > sma)
    se = (c < fib) & (c.shift(1) >= fib) & (c < sma)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
