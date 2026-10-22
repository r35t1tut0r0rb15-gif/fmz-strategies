"""SMA 5 / 20 crossings, 1-hour bars: the SMA 5 crossing over the SMA 20 goes long, under it short; reversing (the 1 % / 2 % bracket is re-sent every bar from the current close and is pending).
Port of FMZ strategy #440517 "金叉死叉双MA策略Double-Moving-Average-Crossover-Strategy" (2MA Cross).

FMZ source id: 440517

Source
    https://www.fmz.com/strategy/440517 (PineScript v5, FMZ last modified 2024-01-31 11:29:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 136-167), long 20, short 5 (SMA; the MA type input is unused); stop 1 %, target 2 %
    crossover(sma5, sma20) -> entry Long;  crossunder -> entry Short;  every bar: strategy.exit(stop = close x 0.99, limit = close x 1.02) for the long (shorts mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent on every bar from that bar's close, so its levels move after entry (1 % /
      2 % from the latest close, active for the next bar): stops() cannot express a level re-set every
      bar, so it is kept pending (as #437036, mark trailing_stop_pending). Positions end at the opposite
      entry until then. The MA type input is never used (both are SMAs). strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent bracket pending.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_440517_sma5_20_cross_resent_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_period": [5, 10],
    "long_period": [20, 50],
}
DEFAULT_PARAMS = {"short_period": 5, "long_period": 20}


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
    s = c.rolling(int(p["short_period"])).mean()
    lg = c.rolling(int(p["long_period"])).mean()
    up = (s > lg) & (s.shift(1) <= lg.shift(1))
    dn = (s < lg) & (s.shift(1) >= lg.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
