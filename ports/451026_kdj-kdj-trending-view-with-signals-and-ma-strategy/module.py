"""KDJ (9, 3) J extremes with close / SMA 20 crossings, 1-hour bars: J at 80 or more with the close crossing under the SMA goes short, J at 20 or less with the close crossing over it goes long; reversing.
Port of FMZ strategy #451026 "KDJ趋势跟踪与信号移动平均策略-KDJ-Trending-View-with-Signals-and-MA-Strategy" (KDJ Trending View with Signals and MA Strategy).

FMZ source id: 451026

Source
    https://www.fmz.com/strategy/451026 (PineScript v5, FMZ last modified 2024-05-11 11:46:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 109-156), KDJ 9 / 3, levels 80 / 20; SMA 20; margins 2 / 2 (unused); qty 1
    kdjJ >= 80 and crossunder(close, sma20) -> entry Short (qty 1);  kdjJ <= 20 and crossover(close, sma20) -> entry Long (qty 1)

Interpretation choices (Pine rules in SURVEY_README.md)
    * K = sma(RSV, 3), D = sma(K, 3), J = 3K - 2D. The margin inputs are never used. No exit:
      positions end at the opposite entry. strategy.entry reverses: REVERSAL INTENDED. The qty 1 is
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, KDJ J extremes with SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the qty 1 stored.
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

NAME = "fmz_451026_kdj_j_extreme_sma20_cross_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "kdj_len": [9, 14],
    "ma_len": [20, 50],
}
DEFAULT_PARAMS = {"kdj_len": 9, "ma_len": 20, "signal": 3, "ob": 80.0, "os": 20.0}


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
    n, s = int(p["kdj_len"]), int(p["signal"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    rsv = 100 * (c - ll) / (hh - ll).where(hh > ll)
    k = rsv.rolling(s).mean()
    d = k.rolling(s).mean()
    j = 3 * k - 2 * d
    ma = c.rolling(int(p["ma_len"])).mean()
    c1 = c.shift(1)
    se = (j >= float(p["ob"])) & (c < ma) & (c1 >= ma.shift(1))
    le = (j <= float(p["os"])) & (c > ma) & (c1 <= ma.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se & ~le, false.copy()


def portfolio_kwargs(**params):
    return {}
