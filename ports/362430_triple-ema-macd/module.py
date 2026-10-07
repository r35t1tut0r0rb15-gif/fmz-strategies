"""MACD(26,49,2) histogram zero crosses in the direction of EMA50 vs EMA200: long on a cross up
with EMA50 above EMA200, short on a cross down below (positions held until the opposite entry).
Port of FMZ strategy #362430 "Triple-EMA-MACD".

Source
    https://www.fmz.com/strategy/362430 (PineScript v4, FMZ last modified 2022-05-11 16:17:19).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 58-99)
    delta = (ema(close,26) - ema(close,49)) - ema(MACD, 2)
    crossover(delta,0) and ema50 > ema200 -> entry long
    crossunder(delta,0) and ema50 < ema200 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Two separate `if`s; they cannot both fire on one bar. strategy.entry reverses:
      REVERSAL INTENDED (portfolio_kwargs {}). default_qty_value 750 is sizing.
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362430_macd_cross_ema_trend"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 26],
    "slow": [49, 60],
    "trend_slow": [150, 200],
}
DEFAULT_PARAMS = {"fast": 26, "slow": 49, "signal": 2, "trend_fast": 50, "trend_slow": 200}


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
    ema = lambda n: c.ewm(span=int(n), adjust=False).mean()
    macd = ema(p["fast"]) - ema(p["slow"])
    delta = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    up_t = ema(p["trend_fast"]) > ema(p["trend_slow"])
    warm = np.arange(len(c)) >= int(p["trend_slow"])
    long_c = ((delta > 0) & (delta.shift(1) <= 0) & up_t).to_numpy() & warm
    short_c = ((delta < 0) & (delta.shift(1) >= 0) & ~up_t).to_numpy() & warm
    return _always_in(long_c, short_c, bars_df.index)


def portfolio_kwargs(**params):
    return {}
