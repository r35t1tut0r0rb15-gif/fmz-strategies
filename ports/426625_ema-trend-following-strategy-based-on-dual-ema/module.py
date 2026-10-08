"""EMA 50 / 200 state (always in): long while EMA 50 is above EMA 200, short while below.
Port of FMZ strategy #426625 "Trend Following Strategy Based on Dual EMA".

Source
    https://www.fmz.com/strategy/426625 (PineScript v4, FMZ last modified 2023-09-13 18:04:52).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 75-87)
    ema50 > ema200 -> entry long (qty 0), close short;  ema50 < ema200 -> entry short (qty 0), close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both entries pass qty = 0. Quantity is sizing, out of the module's scope; read literally no
      order would be sized at all (decision owed). The signal rule is ported.
    * strategy.entry reverses (the closes are then redundant): REVERSAL INTENDED.
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426625_ema_50_200_state"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 50],
    "slow": [100, 200],
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
    d = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    return _always_in((d > 0).to_numpy(), (d < 0).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
