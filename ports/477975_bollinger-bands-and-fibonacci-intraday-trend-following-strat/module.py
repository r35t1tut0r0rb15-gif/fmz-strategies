"""Bollinger 20 / 2 extremes inside the 20-bar Fibonacci range, 10-minute bars: a close under the lower band but above the 23.6 % level goes long, over the upper band but under the 61.8 % level goes short; reversing. The 50 / 100-tick bracket is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #477975 "Bollinger Bands and Fibonacci Intraday Trend Following Strategy" (Bollinger Bands and Fibonacci Intraday Strategy).

FMZ source id: 477975

Source
    https://www.fmz.com/strategy/477975 (PineScript v5, FMZ last modified 2025-01-10 16:29:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-156), BB 20 / 2; Fibonacci 0.236 / 0.382 / 0.618 of the 20-bar range; stop 50, target 100 x mintick from the current close
    fibHigh / fibLow := highest(high, 20) / lowest(low, 20) whenever they change;  close < lower and close > fibLow + 0.236 range -> entry Buy;  close > upper and close < fibLow + 0.618 range -> entry Sell
    every bar: exit(Buy, stop = close - 50 mintick, limit = close + 100 mintick), exit(Sell, mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Fibonacci high / low are reset whenever the 20-bar high / low differ from them, so they are the
      current 20-bar high / low. The bracket is re-sent on every bar from that bar's close, so its levels
      move after entry: stops() cannot express a level re-set every bar, so it is described here and kept
      pending (as #438034, mark trailing_stop_pending). REVERSAL INTENDED. No sizing code. FREQ =
      "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar bracket described (pending).
    2 generic: PASS, Bollinger extremes inside the Fibonacci range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick bracket inputs stored.
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

NAME = "fmz_477975_bb20_extreme_fib_range_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "fib_len": 20}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    k = int(p["fib_len"])
    fh, fl = h.rolling(k).max(), lo.rolling(k).min()
    f236 = fl + (fh - fl) * 0.236
    f618 = fl + (fh - fl) * 0.618
    le = (c < basis - dev) & (c > f236)
    se = (c > basis + dev) & (c < f618)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
