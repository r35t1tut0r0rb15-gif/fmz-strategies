"""SMA 10 / 50 cross, 1-hour bars: a golden cross goes long, a death cross goes short; as written only the short carries the
1 % stop (both stop exits share one id and are re-issued every bar, the short's last), fixed at the fill here.
Port of FMZ strategy #430658 "trend following strategy based on moving averages" (Simple Moving Average Crossover).

FMZ source id: 430658

Source
    https://www.fmz.com/strategy/430658 (PineScript v4, FMZ last modified 2023-10-31 14:00:47).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 162-195), SMA 10 / 50, stop 1 %
    crossover(sma10, sma50) -> entry long;  crossunder -> entry short
    every bar: exit("Stop Loss/Profit", "Long", stop = close x 0.99); exit("Stop Loss/Profit", "Short", stop = close x 1.01)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The shared exit id is re-bound to the short entry on every bar, so a long has no stop and a
      short has one (as #430368). The level follows each bar's close (moving): rule 2, mark
      trailing_stop_pending; the port fixes it at 1 % of the fill for shorts.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the shared-id exit read as written, the moving stop fixed at the fill.
    2 generic: PASS, moving averages and a percentage stop.
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

NAME = "fmz_430658_sma10_50_cross_short_stop"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [10, 20],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 50, "stop_pct": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _signals(bars_df, p):
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    xo = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    xu = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    return xo, xu


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, short_e = _signals(bars_df, p)
    sl = pd.Series(np.where(short_e, float(p["stop_pct"]) / 100, np.nan), index=bars_df.index)
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
