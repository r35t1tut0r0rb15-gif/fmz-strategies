"""MACD (12, 26) outside its own Bollinger band (10, 1), 1-hour bars: the MACD above its upper band goes long, below its lower band goes short; reversing (the take-profit / stop lines are commented out).
Port of FMZ strategy #449446 "MACD-BB-波段突破策略-MACD-BB-Breakout-Strategy" (AK MACD BB strategy).

FMZ source id: 449446

Source
    https://www.fmz.com/strategy/449446 (PineScript v5, FMZ last modified 2024-04-25 17:16:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-152), MACD 12 / 26; band on the MACD: SMA 10 +- 1 sd; TP / SL 1 % (commented out)
    macd > sma(macd, 10) + sd(macd, 10) -> entry Long;  macd < sma - sd -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both conditions are levels, so a repeated entry while already on that side is ignored. The
      bracket calls are commented out: positions end at the opposite entry. Pine's stdev is the
      population deviation. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD band breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_449446_macd_own_band_breakout_reversal"
FAMILY = "macd_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "dev": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 10, "dev": 1.0, "fast": 12, "slow": 26}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    n = int(p["length"])
    sd = macd.rolling(n).std(ddof=0)
    mid = macd.rolling(n).mean()
    upper = mid + sd * float(p["dev"])
    lower = mid - sd * float(p["dev"])
    le = macd > upper
    se = macd < lower
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
