"""Matrix Series: a z-score-like oscillator of the weighted price, smoothed three times; when its
smoothed line is above +200 (overbought) go LONG, below -200 go SHORT, as written (always in).
Port of FMZ strategy #365381 "Matrix Series".

Source
    https://www.fmz.com/strategy/365381 (PineScript, mixed v4/v5 syntax, FMZ last modified
    2022-05-24 16:42:26). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 48-108), smoother 5, levels +-200
    ys = (high + low + 2 close) / 4;  rk5 = (ys - ema(ys, 5)) * 200 / stdev(ys, 5)
    up = ema(ema(rk5, 5), 5);  down = ema(up, 5)
    UPshape = up > 200 and up != down (a positive value) -> entry long
    else DOWNshape = down < -200 and up != down -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The shapes are plotted values (non-zero when defined), so they act as booleans; when
      up == down neither branch defines them.
    * Overbought enters long and oversold short: kept as written. The CCI support/resistance
      lines only draw.
    * Population stdev. strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "15min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365381_matrix_series_extreme"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "smoother": [3, 5, 8],
    "level": [100, 200],
}
DEFAULT_PARAMS = {"smoother": 5, "level": 200}


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
    n = int(p["smoother"])
    ys = (bars_df["high"] + bars_df["low"] + bars_df["close"] * 2) / 4
    ema = lambda x: x.ewm(span=n, adjust=False).mean()
    rk5 = (ys - ema(ys)) * 200 / ys.rolling(n).std(ddof=0)
    up = ema(ema(rk5))
    down = ema(up)
    lvl = p["level"]
    long_ = ((up > lvl) & (up != down)).to_numpy()
    short = ((down < -lvl) & (up != down)).to_numpy()
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
