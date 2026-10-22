"""SMA 10 / 30 cross-ups, 1-hour bars, long only: the cross up buys with a take-profit 6 price units over the signal close (0.000143 of the fill at BTC 42000); there is no other exit.
Port of FMZ strategy #452821 "Moving Average Crossover with Trailing Stop Loss Strategy" (AAPL-SIMPLE_SMA).

FMZ source id: 452821

Source
    https://www.fmz.com/strategy/452821 (PineScript v5, FMZ last modified 2024-05-29 17:02:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-126), SMA 10 / 30; take profit close + 6 (the stop close - 2 only in the alert text); quantity 1
    crossover(sma10, sma30) -> entry long, exit(limit = close + 6)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target is a price amount: read against BTC near 42000 like other price units (#440456), it is
      ported as the fraction 6 / 42000 of the fill. The stop (close - 2) only appears in the alert
      string; the exit with it is commented out. A repeat cross-up inside a trade (after a cross down,
      which does not close) re-issues the target from that bar's close, which stops() cannot express:
      the port keeps the opening level and marks trailing_stop_pending (as #434428). Long only. Stop
      module: portfolio_kwargs {} (driver D4). The quantity 1 is sizing. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the price-unit target as a fraction of 42000; re-issued target pending (mark).
    2 generic: PASS, SMA cross-ups with a fixed target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity 1 stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_452821_sma10_30_cross_up_price_unit_target_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [10, 20],
    "slow": [30, 50],
    "tp_frac": [0.000143, 0.01],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30, "tp_frac": 0.000143}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
