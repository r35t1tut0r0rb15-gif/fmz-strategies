"""Double Bollinger bands (SMA 20 with 2 and 3 sd), hourly bars: the close crossing back over the lower 3-sd band goes long and crossing over the upper 2-sd band closes it; the close crossing back under the upper 3-sd band goes short and crossing under the lower 2-sd band closes it; reversing.
Port of FMZ strategy #484919 "Double Bollinger Bands Extreme Reversal Trading Strategy" (Double Bollinger Bands Strategy with Signals (By Rolwin)).

FMZ source id: 484919

Source
    https://www.fmz.com/strategy/484919 (PineScript v5, FMZ last modified 2025-03-05 10:10:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 193-242), Bollinger 20 with 2.0 and 3.0 sd
    crossover(close, lower3) -> entry Long;  crossunder(close, upper3) -> entry Short
    crossover(close, upper2) -> close Long;  crossunder(close, lower2) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close on the bar of an entry is masked by the entry; an entry on the other side reverses
      (REVERSAL INTENDED). The bar colours are drawing only. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, double Bollinger band re-entries and exits.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
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

NAME = "fmz_484919_double_bb20_3sd_reentry_2sd_exit_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "bb2_mult": [3.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "bb2_mult": 3.0, "bb1_mult": 2.0}


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
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    u1, l1 = basis + float(p["bb1_mult"]) * sd, basis - float(p["bb1_mult"]) * sd
    u2, l2 = basis + float(p["bb2_mult"]) * sd, basis - float(p["bb2_mult"]) * sd
    le = (c > l2) & (c.shift(1) <= l2.shift(1))
    se = (c < u2) & (c.shift(1) >= u2.shift(1))
    lx = (c > u1) & (c.shift(1) <= u1.shift(1))
    sx = (c < l1) & (c.shift(1) >= l1.shift(1))
    return le & ~se, lx & ~le & ~se, se, sx & ~se & ~le


def portfolio_kwargs(**params):
    return {}
