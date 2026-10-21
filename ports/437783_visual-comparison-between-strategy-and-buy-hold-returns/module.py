"""SMA 50 / 200 crossings, 3-minute bars: the SMA 50 crossing over the SMA 200 goes long, crossing under goes short; reversing. The strategy-versus-buy-and-hold panel only plots.
Port of FMZ strategy #437783 "Visual Comparison between Strategy and Buy Hold Returns" (VS Buy Hold).

FMZ source id: 437783

Source
    https://www.fmz.com/strategy/437783 (PineScript v4, FMZ last modified 2024-01-05 15:27:26).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 157-231), SMA 50 / 200 (fixed); comparison window 1970-2050 (always true); quantity capital 50000 / close
    crossover(sma 50, sma 200) and timeCond -> entry long;  crossunder(sma 50, sma 200) and timeCond -> entry short;  strategy and buy-and-hold returns plotted only

Interpretation choices (Pine rules in SURVEY_README.md)
    * The comparison window covers all data (true). The quantity initial_capital / close is sizing. The
      buy-and-hold comparison and its counters only plot. strategy.entry reverses: REVERSAL INTENDED.
      FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital / close quantity stored.
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

NAME = "fmz_437783_sma50_200_cross_vs_buyhold"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 20],
    "slow": [200, 100],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200}


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
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
