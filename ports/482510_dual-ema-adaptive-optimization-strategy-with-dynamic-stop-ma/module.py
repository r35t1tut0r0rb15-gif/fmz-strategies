"""EMA 5 / 10 crosses, reversing, with a 1 % stop and a 1 % target from the signal close, hourly bars.
Port of FMZ strategy #482510 "双均线自适应优化策略与动态止盈止损系统-Dual-EMA-Adaptive-Optimization-Strategy-with-Dynamic-Stop-Management-System" (Evolutivna Strategija - AI Optimizacija).

FMZ source id: 482510

Source
    https://www.fmz.com/strategy/482510 (PineScript v5, FMZ last modified 2025-02-18 18:14:10).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 87-115), EMA 5 / 10, SL 1 %, TP 1 %
    "best" SL / TP := the inputs whenever net profit makes a new high (always the inputs)
    crossover -> entry long with exit(stop = close x 0.99, limit = close x 1.01); crossunder -> short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "optimisation" only ever copies the inputs, so the bracket is the fixed 1 % / 1 % (as written).
    * The bracket is placed with the entry from the signal close, re-based on the fill (house rule).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, two EMAs and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity; the bracket via stops(), quoted in original_sizing.txt.
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

NAME = "fmz_482510_ema5_10_cross_pct_bracket"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [1.0, 2.0],
    "tp_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 10, "sl_pct": 1.0, "tp_pct": 1.0}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
