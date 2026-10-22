"""The 09:15 UTC 15-minute candle's range, 15-minute bars: once captured, a close above its high goes long and a close below its low goes short, the range renewing each day at 09:15; reversing.
Port of FMZ strategy #478700 "基于15分钟突破的高效价格通道交易策略-Efficient-Price-Channel-Trading-Strategy-Based-on-15-Minute-Breakout" (15 Min Breakout Strategy).

FMZ source id: 478700

Source
    https://www.fmz.com/strategy/478700 (PineScript v5, FMZ last modified 2025-01-17 14:49:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-141), first candle 09:15 (exchange time); 100 % of equity; close_all before 2023-01-01
    hour == 9 and minute == 15 -> firstHigh := high, firstLow := low, captured := true;  captured and close > firstHigh -> entry Buy Signal;  captured and close < firstLow -> entry Sell Signal;  time < 2023-01-01 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The capture bar is the 15-minute bar opening at 09:15 UTC (the header market's exchange time), with
      no DST; the flag never clears, so after the first capture the close is always compared with the
      latest 09:15 range. The entries are states and repeat; a repeat on the held side is ignored. The
      close_all before 2023-01-01 is a backtest start date and is not ported. REVERSAL INTENDED. The 100 %
      of equity size is sizing. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, opening-range breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: capture bar 09:15 UTC (fixed UTC, no DST).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_478700_0915utc_candle_range_breakout_reversal"
FAMILY = "opening_range"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "capture_hour": [9, 13],
    "capture_minute": [15, 30],
}
DEFAULT_PARAMS = {"capture_hour": 9, "capture_minute": 15}


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
    t = c.index.tz_convert("UTC")
    cap = np.asarray((t.hour == int(p["capture_hour"])) & (t.minute == int(p["capture_minute"])))
    idx = np.where(cap, np.arange(len(cap)), 0)
    idx = np.maximum.accumulate(idx)
    seen = np.maximum.accumulate(cap)
    fh = np.where(seen, h.to_numpy(dtype=float)[idx], np.nan)
    fl = np.where(seen, lo.to_numpy(dtype=float)[idx], np.nan)
    cv = c.to_numpy(dtype=float)
    ix = c.index
    le = pd.Series(seen & (cv > fh), index=ix)
    se = pd.Series(seen & (cv < fl), index=ix)
    false = pd.Series(False, index=ix)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
