"""One-sd Bollinger (20) breakouts, 1-hour bars: the close crossing over SMA + 1 sd goes long, crossing under SMA - 1 sd goes short; the close crossing back through the SMA closes; reversing.
Port of FMZ strategy #449961 "Bollinger-Bands-Standard-Deviation-Breakout-Strategy-布林带标准差突破策略" (MBB (Bollinger Bands, Madrid one-sd breakout)).

FMZ source id: 449961

Source
    https://www.fmz.com/strategy/449961 (PineScript v5, FMZ last modified 2024-04-30 16:51:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-150), SMA 20; bands 1 sd (trades) and 2 sd (plot only)
    crossover(close, upper1) -> entry Long;  crossunder(close, lower1) -> entry Short;  crossunder(close, basis) -> close Long;  crossover(close, basis) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes come after the entries: a close after a reversing entry on the same bar leaves the
      reversal. Pine's stdev is the population deviation. REVERSAL INTENDED. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, one-sd band breakouts with basis exits.
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

NAME = "fmz_449961_one_sd_band_breakout_basis_exit_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "k": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "k": 1.0}


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
    upper = basis + float(p["k"]) * sd
    lower = basis - float(p["k"]) * sd
    c1 = c.shift(1)
    le = (c > upper) & (c1 <= upper.shift(1))
    se = (c < lower) & (c1 >= lower.shift(1))
    xb_dn = (c < basis) & (c1 >= basis.shift(1))
    xb_up = (c > basis) & (c1 <= basis.shift(1))
    return le, xb_dn & ~se, se, xb_up & ~le


def portfolio_kwargs(**params):
    return {}
