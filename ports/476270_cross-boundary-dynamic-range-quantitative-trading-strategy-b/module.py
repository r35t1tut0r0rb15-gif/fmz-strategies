"""Bollinger 20 / 2 re-entries, 3-hour bars, long only: the close crossing back over the lower band buys, crossing back under the upper band closes.
Port of FMZ strategy #476270 "Cross boundary Dynamic Range Quantitative Trading Strategy Based on Bollinger Bands" (Bollinger Bands Strategy).

FMZ source id: 476270

Source
    https://www.fmz.com/strategy/476270 (PineScript v5, FMZ last modified 2024-12-27 15:39:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 79-132), BB 20 / 2; qty = 86 USDT / close; capital 86
    crossover(close, lower) and usdt_balance > 0 -> entry Buy (qty = usdt_balance / close);  crossunder(close, upper) and zerebro_balance > 0 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * usdt_balance (86) and zerebro_balance (52) are declared without var, so they are reset on every bar
      and both balance tests always pass. Long only. The 86-USDT order size and capital are sizing. FREQ =
      "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger band re-entries.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 86 USDT / close and capital 86 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_476270_bb20_lower_reentry_upper_reentry_close_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


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
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    le = (c > dn) & (c.shift(1) <= dn.shift(1))
    lx = (c < up) & (c.shift(1) >= up.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
