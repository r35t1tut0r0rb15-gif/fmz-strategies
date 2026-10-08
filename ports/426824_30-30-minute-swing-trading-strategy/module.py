"""Hull slope (always in): long while the Hull MA (70) of the close is above its value one bar
back, short while at or below it.
Port of FMZ strategy #426824 "30 Minute Swing Trading Strategy".

Source
    https://www.fmz.com/strategy/426824 (PineScript v2/v3 syntax, FMZ last modified 2023-09-14 17:44:03).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 131-197), period 70
    n1 = wma(2 wma(close, round(70 / 2)) - wma(close, 70), round(sqrt(70)))
    n2 = the same on close[1]
    condDown = n2 >= n1; condUp = condDown != true
    condUp -> entry long, else condDown -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * While n1 / n2 are na, n2 >= n1 is false, so condUp holds and the source is long (as Pine).
    * The RSI / EMA inputs and the stop value only feed unused variables.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2h" from the backtest header (the title's 30 minutes is not the backtest period).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426824_hull_slope"
FAMILY = "slope_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [35, 70, 100],
}
DEFAULT_PARAMS = {"period": 70}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


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


def _hull(x, n):
    return _wma(2 * _wma(x, int(round(n / 2))) - _wma(x, n), int(round(np.sqrt(n))))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["period"])
    n1, n2 = _hull(c, n), _hull(c.shift(1), n)
    down = (n2 >= n1).to_numpy()
    return _always_in(~down, down, bars_df.index)


def portfolio_kwargs(**params):
    return {}
