"""Demark setup [CC]: four consecutive lower closes than four bars earlier (on the previous bar's
close series) is a buy setup; the DSI turning positive goes long, turning negative goes short.
Port of FMZ strategy #366947 "Demark Setup Indicator [CC]".

Source
    https://www.fmz.com/strategy/366947 (PineScript v4, FMZ last modified 2022-05-31 19:29:50).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 49-75), length 4, repainting off, resolution ""
    src = security(chart, close)[1]   (historical bars: the previous close)
    uCount = #{i < 4: nz(src[i]) > nz(src[i + 4])};  dCount likewise with <
    dsi = dCount == 4 ? 1 : uCount == 4 ? -1 : 0
    crossover(dsi, 0) -> entry long; else crossunder(dsi, 0) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * With repainting off, historical bars read the series one bar back ([1]); kept (it only
      delays the setup by a bar). nz() makes missing history 0, as coded.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366947_demark_setup_turn"
FAMILY = "td_sequential"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [3, 4, 6, 9],
}
DEFAULT_PARAMS = {"length": 4}


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
    n = int(p["length"])
    src = bars_df["close"].shift(1)
    nz = lambda s: s.fillna(0.0)
    up = sum((nz(src.shift(i)) > nz(src.shift(i + n))).astype(int) for i in range(n))
    dn = sum((nz(src.shift(i)) < nz(src.shift(i + n))).astype(int) for i in range(n))
    dsi = np.where(dn == n, 1, np.where(up == n, -1, 0))
    prev = np.concatenate([[0], dsi[:-1]])
    return _always_in((dsi > 0) & (prev <= 0), (dsi < 0) & (prev >= 0), bars_df.index)


def portfolio_kwargs(**params):
    return {}
