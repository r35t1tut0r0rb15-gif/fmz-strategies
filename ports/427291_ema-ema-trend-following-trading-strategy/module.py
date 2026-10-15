"""EMA 12 / 26 cross, long only: the fast EMA crossing above the slow one goes long, crossing back
under closes the long.
Port of FMZ strategy #427291 "EMA Trend Following Trading Strategy".

FMZ source id: 427291

Source
    https://www.fmz.com/strategy/427291 (PineScript v5, FMZ last modified 2023-09-19 19:38:53).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 160-194)
    crossover(ema(close, 12), ema(close, 26)) -> entry long; crossunder -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * inTradeWindow is the constant true (the 2021 date filter was replaced by FMZ): no window,
      and the "Date Range Exit" never fires.
    * Long only; entries only from flat.
    * FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (a BTC-quoted pair in the header only).
    4 signals only: initial capital / BTC currency stored in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427291_ema_12_26_long"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 50, 100],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26}


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
    up = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, dn, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
