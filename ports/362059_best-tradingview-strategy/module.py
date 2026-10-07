"""SMA(14) vs SMA(42) trend with a close crossing the lower Bollinger band: long on a cross up
in an up-trend, short on a cross down in a down-trend; a trailing exit is armed on the opposite
SMA cross (trailing part pending).
Port of FMZ strategy #362059 "Best-TradingView-Strategy".

Source
    https://www.fmz.com/strategy/362059 (PineScript v5, FMZ last modified 2022-05-09 21:42:21).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 57-146), BB 15 x 2
    long  = sma(close,14) > sma(close,42) and crossover(close, lowerBB)  -> entry long
    short = sma(close,14) < sma(close,42) and crossunder(close, lowerBB) -> entry short
    strategy.exit(trail_points=100, trail_offset=50) armed when sma42 crosses over sma14 (long)
    / sma14 crosses over sma42 (short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries reverse an opposite position: REVERSAL INTENDED (portfolio_kwargs {}).
    * The only other exit is a tick-based trailing stop: rule 2, mark trailing_stop_pending,
      described in PORT_NOTES; not emitted. Without it positions run until the opposite entry.
    * RSI and ADX are computed but unused by the orders.
    * FREQ = "15min" from the backtest header.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_362059_sma_trend_bb_lower_cross"
FAMILY = "bollinger_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_len": [15, 20],
    "bb_mult": [2.0, 2.5],
    "slow_sma": [42, 84],
}
DEFAULT_PARAMS = {"bb_len": 15, "bb_mult": 2.0, "fast_sma": 14, "slow_sma": 42}


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
    n = int(p["bb_len"])
    lower = c.rolling(n).mean() - p["bb_mult"] * c.rolling(n).std(ddof=0)
    out = c.rolling(int(p["fast_sma"])).mean()
    slow = c.rolling(int(p["slow_sma"])).mean()
    up = ((out > slow) & (c > lower) & (c.shift(1) <= lower.shift(1))).to_numpy()
    dn = ((out < slow) & (c < lower) & (c.shift(1) >= lower.shift(1))).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
