"""EMA(55) vs Kijun-sen(26) crosses traded as written: EMA crossing DOWN through the Kijun goes
LONG, crossing UP goes SHORT (always in).
Port of FMZ strategy #362427 "Playing-the-cross".

Source
    https://www.fmz.com/strategy/362427 (PineScript v5, FMZ last modified 2022-05-11 15:07:20).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 51-76)
    KijunSen = avg(lowest(26), highest(26)); MA = ema(close, 55)
    Down = MA < Kijun and MA[1] > Kijun[1] -> entry long;  else Up -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * No backtest header: FREQ = "bar_size_pending" (rule 1).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_362427_ema_kijun_cross_faded"
FAMILY = "ichimoku"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # source declares no bar size; set by the project before running
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "kijun": [9, 26, 52],
    "ema_len": [34, 55, 89],
}
DEFAULT_PARAMS = {"kijun": 26, "ema_len": 55}


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
    n = int(p["kijun"])
    kij = (bars_df["low"].rolling(n).min() + bars_df["high"].rolling(n).max()) / 2
    ma = bars_df["close"].ewm(span=int(p["ema_len"]), adjust=False).mean()
    down = ((ma < kij) & (ma.shift(1) > kij.shift(1))).to_numpy()
    up = ((ma > kij) & (ma.shift(1) < kij.shift(1))).to_numpy()
    return _always_in(down, up, bars_df.index)


def portfolio_kwargs(**params):
    return {}
