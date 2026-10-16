"""SMA 200 cross with a percent bracket, long only: the close crossing above SMA 200 goes long; the
position exits at a 2 % stop or a 1 % target from the entry price.
Port of FMZ strategy #427821 "Percentage Stop Loss Take Profit Trailing Strategy".

FMZ source id: 427821

Source
    https://www.fmz.com/strategy/427821 (PineScript v3, FMZ last modified 2023-09-25 18:09:14).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 181-195), SMA 200, stop 2 %, target 1 %
    crossover(close, sma(close, 200)) -> entry long
    exit(stop = avg price x (1 - 2 %), limit = avg price x (1 + 1 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * Percent-of-entry levels stay fractions: sl_stop 0.02, tp_stop 0.01 (nothing trails despite
      the title).
    * Stop module: portfolio_kwargs {} (driver D4). Long only.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close entries; bracket fixed at entry.
    2 generic: PASS, percentages only.
    3 crypto-exchange-only: no (spot pair in the header only).
    4 signals only: no sizing code; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import pandas as pd

NAME = "fmz_427821_sma200_cross_pct_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sma_per": [200, 100],
    "sl_pct": [2.0, 1.0],
    "tp_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"sma_per": 200, "sl_pct": 2.0, "tp_pct": 1.0}


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
    s = c.rolling(int(p["sma_per"])).mean()
    long_e = ((c > s) & (c.shift(1) <= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100, "tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
