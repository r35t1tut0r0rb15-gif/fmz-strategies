"""Bollinger (51, 3.01) as written: the close crossing down through the upper band goes long and
crossing up through the lower band goes short; each entry carries a 14.2 % target and a 99 %
stop.
Port of FMZ strategy #426848 "Medium Long Term Quantitative Trading Strategy Based on Bollinger".

Source
    https://www.fmz.com/strategy/426848 (PineScript v2/v3 syntax, FMZ last modified 2023-09-14 20:09:13).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 162-211), length 51, mult 3.01, target 14.2 %, stop 99 %
    short_cond = crossover(close, lower);  long_cond = crossunder(close, upper)
    long_cond  -> entry long,  exit(profit = close * 14.2 % * 10, loss = close * 99 % * 10)
    short_cond -> entry short, exit(the same)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Kept as written: long on a fall through the upper band, short on a rise through the lower
      one (the names suggest the reverse; decision owed).
    * profit / loss are ticks; x 10 makes them 14.2 % / 99 % of the signal close on a 0.1 tick
      (BTC_USDT perpetual), so they are ported as tp_stop 14.2 % and sl_stop 99 % of the fill.
    * The cl average only plots. strategy.entry reverses: REVERSAL INTENDED; entries do not
      depend on the position, so nothing needs mirroring.
    * stdev is Pine's population deviation. FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426848_bollinger_inverted_bracket"
FAMILY = "bollinger_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [21, 51],
    "mult": [2.0, 3.01],
    "tp_pct": [5.0, 14.2],
}
DEFAULT_PARAMS = {"length": 51, "mult": 3.01, "tp_pct": 14.2, "sl_pct": 99.0}


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
    n = int(p["length"])
    base = c.rolling(n).mean()
    rng = p["mult"] * c.rolling(n).std(ddof=0)
    upper, lower = base + rng, base - rng
    se = (c > lower) & (c.shift(1) <= lower.shift(1))
    le = (c < upper) & (c.shift(1) >= upper.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
