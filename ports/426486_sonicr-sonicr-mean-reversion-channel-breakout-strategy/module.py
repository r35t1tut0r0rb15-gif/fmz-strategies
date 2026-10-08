"""SonicR EMA cross (always in): EMA 34 of the close crossing above EMA 89 goes long, crossing
below goes short.
Port of FMZ strategy #426486 "SonicR Mean Reversion Channel Breakout Strategy".

Source
    https://www.fmz.com/strategy/426486 (PineScript v2/v3 syntax, FMZ last modified 2023-09-12 15:09:57).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 106-124), EMA signal 89, channel 34
    crossover(ema(close, 34), ema(close, 89)) -> entry long;  crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The high / low channel EMAs only plot.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426486_sonicr_ema_cross"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hilo_len": [21, 34],
    "ema_signal": [89, 144],
}
DEFAULT_PARAMS = {"hilo_len": 34, "ema_signal": 89}


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
    d = c.ewm(span=int(p["hilo_len"]), adjust=False).mean() - c.ewm(span=int(p["ema_signal"]), adjust=False).mean()
    d1 = d.shift(1)
    return _always_in(((d > 0) & (d1 <= 0)).to_numpy(), ((d < 0) & (d1 >= 0)).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
