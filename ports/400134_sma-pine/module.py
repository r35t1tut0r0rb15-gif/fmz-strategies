"""SMA cross teaching script (Zer3192): SMA 10 crossing above SMA 200 goes long, below goes short;
every position has a 5 % stop and a 5 % target on its entry price.
Port of FMZ strategy #400134 "SMA-pine语言教学策略脚本" (SMA Cross).

Source
    https://www.fmz.com/strategy/400134 (PineScript v4, author Zer3192, FMZ last modified
    2023-02-15 18:19:03). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 19-51)
    crossover(sma10, sma200) -> entry long;  crossunder -> entry short
    long: exit(stop = avg * 0.95, limit = avg * 1.05);  short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are fixed fractions of the entry price: stops() returns sl_stop = tp_stop = 0.05,
      shifted one bar inside stops() (constant, so the shift only blanks the first bar).
    * The exit lines are not indented under their ifs; they run every bar, which is the same
      thing while a position exists.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * No bar size in the source: FREQ = "bar_size_pending" (rule 1, 2026-10-07).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_400134_sma_10_200_bracket"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # no bar size in the source (rule 1, 2026-10-07)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [10, 20],
    "slow": [100, 200],
    "pct": [0.03, 0.05],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 200, "pct": 0.05}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(up, index=idx), false.copy(), pd.Series(dn, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    pct = pd.Series(float(p["pct"]), index=bars_df.index)
    return {"sl_stop": pct.shift(1), "tp_stop": pct.shift(1)}


def portfolio_kwargs(**params):
    return {}
