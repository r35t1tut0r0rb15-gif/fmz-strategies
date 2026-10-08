"""Percent distance from SMA 14 (HPotter, always in): a close within 0.03 % of SMA 14 goes long,
one more than 0.54 % away (either side) goes short.
Port of FMZ strategy #426774 "Moving Average Percentage Reversal Strategy".

Source
    https://www.fmz.com/strategy/426774 (PineScript v2/v3 syntax, FMZ last modified 2023-09-14 14:53:53).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 125-140), Length 14, SellZone 0.54, BuyZone 0.03
    nRes = |close - sma(close, 14)| * 100 / close
    pos = nRes < 0.03 ? 1 : nRes > 0.54 ? -1 : previous;  1 -> entry long, -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The distance is absolute, so "short" also fires far above the SMA (as written).
    * "Trade reverse" off. strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426774_ma_percent_distance"
FAMILY = "ma_envelope_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 28],
    "sell_zone": [0.54, 1.0],
    "buy_zone": [0.03, 0.1],
}
DEFAULT_PARAMS = {"length": 14, "sell_zone": 0.54, "buy_zone": 0.03}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    res = (c - c.rolling(int(p["length"])).mean()).abs() * 100 / c
    return _always_in((res < p["buy_zone"]).to_numpy(), (res > p["sell_zone"]).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
