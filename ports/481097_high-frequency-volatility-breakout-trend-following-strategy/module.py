"""Bollinger 20 / 2 re-entries on the side of the SMA 20, 4-hour bars: the close crossing back over the lower band while above the SMA goes long, back under the upper band while below it goes short; the close on the other side of the SMA closes; reversing.
Port of FMZ strategy #481097 "High Frequency Volatility Breakout Trend Following Strategy" (Bollinger Bands + Moving Average Strategy).

FMZ source id: 481097

Source
    https://www.fmz.com/strategy/481097 (PineScript v5, FMZ last modified 2025-02-08 14:56:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-158), MA SMA 20; BB 20 / 2; 200 % of equity
    crossover(close, lower) and close > sma20 -> entry Long;  crossunder(close, upper) and close < sma20 -> entry Short;  crossunder(close, sma20) or close < sma20 -> close Long;  crossover or close > sma20 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The MA and the band basis are the same SMA 20, so a long needs the close to jump from under the lower
      band to above the basis in one bar, as written. The closes are states; a close acts only on the
      held position and leaves a same-bar reversal standing (as #441963). REVERSAL INTENDED. The 200 % of
      equity size is sizing. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger re-entries on the SMA side with SMA closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity stored, not ported.
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

NAME = "fmz_481097_bb20_reentry_sma20_side_close_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_period": [20, 50],
    "bb_mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"bb_period": 20, "bb_mult": 2.0, "ma_period": 20}


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
    ma = c.rolling(int(p["ma_period"])).mean()
    n = int(p["bb_period"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    le = (c > dn) & (c.shift(1) <= dn.shift(1)) & (c > ma)
    se = (c < up) & (c.shift(1) >= up.shift(1)) & (c < ma)
    lx = (c < ma) & ~se
    sx = (c > ma) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
