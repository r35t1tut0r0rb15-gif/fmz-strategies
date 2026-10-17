"""SMA 9 / 21 crosses with a 1 % stop / 2 % target, 1-hour bars: SMA 9 crossing above SMA 21 goes long; crossing
below goes short.
Port of FMZ strategy #483026 "智能双均线交叉风险管理交易系统-Intelligent-Dual-SMA-Crossover-Risk-Management-Trading-System" (AI Trade Bot with Risk Management).

FMZ source id: 483026

Source
    https://www.fmz.com/strategy/483026 (PineScript v6, FMZ last modified 2025-02-21 09:56:11).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 100-134), SMA 9 / 21, risk 1 % (stop 1 %, target 2 %)
    long = crossover(sma9, sma21); entry + exit(limit = close x 1.02, stop = close x 0.99) (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal close: 1 % / 2 % fractions re-based on the fill (house
      rule). Crosses alternate, so a same-side signal while held cannot occur: no re-placement.
    * The "risk percentage" sets the stop distance (a signal parameter), not the size; riskAmount is unused.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar.
    2 generic: PASS, moving averages and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (riskAmount unused); the bracket via stops(), quoted in original_sizing.txt.
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

NAME = "fmz_483026_sma9_21_cross_pct_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "risk_pct": [1.0, 2.0],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "risk_pct": 1.0}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = p["risk_pct"] / 100
    return {"sl_stop": sl, "tp_stop": 2 * sl}


def portfolio_kwargs(**params):
    return {}
