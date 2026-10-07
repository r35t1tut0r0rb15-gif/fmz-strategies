"""EMA20 vs EMA50 side (always in): long while the fast EMA is above the slow one, short while
below. The swing-high/low and MACD markers of the indicator do not send orders.
Port of FMZ strategy #362443 "Swing-High-Low-Indicator-w-MACD-and-EMA-Confirmations".

Source
    https://www.fmz.com/strategy/362443 (PineScript v4, FMZ last modified 2022-05-11 16:33:11).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 70-173), EMA 20/50 on res "240", chart 4h
    femaSmooth/semaSmooth = security(tickerid, "240", ema(close,20/50)[0 historically])
    uptrend -> entry long;  else downtrend -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The requested resolution (240) equals the chart's (4h), so the request returns the chart's
      own EMAs (no lookahead; the [1] offset applies only to realtime bars).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362443_ema_20_50_side"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 20, 30],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    warm = np.arange(len(c)) >= int(p["slow"])
    return _always_in((f > s).to_numpy() & warm, (f < s).to_numpy() & warm, bars_df.index)


def portfolio_kwargs(**params):
    return {}
