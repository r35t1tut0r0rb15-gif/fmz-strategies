"""3-EMA pullback zone: in an ordered up-trend (20 > 50 > 100, EMA50 rising) a close between
EMA50 and EMA20 goes long; the mirror goes short (always in).
Port of FMZ strategy #362572 "3EMA".

Source
    https://www.fmz.com/strategy/362572 (PineScript v5, FMZ last modified 2022-05-12 01:35:20).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 41-78), EMA 20 / 50 / 100
    long area  = ema20 > ema50 > ema100 and rising(ema50, 2) and ema50 < close <= ema20
    short area = ema20 < ema50 < ema100 and falling(ema50, 2) and ema20 < close <= ema50
    long area -> entry long;  else short area -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * rising(x, 2): x above both of its previous two values.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362572_three_ema_pullback_zone"
FAMILY = "ma_trend_oscillator_pullback"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short": [10, 20],
    "mid": [50, 60],
    "long": [100, 200],
}
DEFAULT_PARAMS = {"short": 20, "mid": 50, "long": 100}


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
    s, m_, l = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("short", "mid", "long"))
    rising = (m_ > m_.shift(1)) & (m_ > m_.shift(2))
    falling = (m_ < m_.shift(1)) & (m_ < m_.shift(2))
    long_a = ((s > m_) & (m_ > l) & rising & (c > m_) & (c <= s)).to_numpy()
    short_a = ((s < m_) & (m_ < l) & falling & (c <= m_) & (c > s)).to_numpy()
    warm = np.arange(len(c)) >= int(p["long"])
    return _always_in(long_a & warm, short_a & warm, bars_df.index)


def portfolio_kwargs(**params):
    return {}
