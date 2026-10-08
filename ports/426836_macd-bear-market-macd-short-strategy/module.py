"""Bear MACD short (Coinrule): below EMA 450, a MACD (11 / 26 / 9) cross under its signal goes
short with a stop 4 % above the signal bar's high and a target 8 % under its low.
Port of FMZ strategy #426836 "Bear Market MACD Short Strategy".

Source
    https://www.fmz.com/strategy/426836 (PineScript v5, FMZ last modified 2023-09-14 18:04:28).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 121-138), EMA 450, MACD 11 / 26 / 9
    crossunder(macd, signal) and ema450 > close and position <= 0 -> entry short,
        exit(stop = high * 1.04, limit = low * 0.92)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels come from the signal bar; as fractions of its close they are applied to the fill
      (sl_stop = 1.04 high / close - 1, tp_stop = 1 - 0.92 low / close, shifted one bar).
    * A signal while short is refused by Pine and the engine alike: no mirroring.
    * The start date (2021-12-01) is a backtest window: dropped.
    * Short only. Opposite entries cannot occur. FREQ = "2h" from the backtest header; stops on
      2h bars: coarse_bar_stop.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_426836_bear_macd_short"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [200, 450],
    "stop_pct": [2.0, 4.0],
    "target_pct": [8.0, 4.0],
}
DEFAULT_PARAMS = {"ema_len": 450, "fast": 11, "slow": 26, "signal": 9, "stop_pct": 4.0, "target_pct": 8.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _short_signal(bars_df, p):
    c = bars_df["close"]
    ema = lambda x, n: x.ewm(span=int(n), adjust=False).mean()
    macd = ema(c, p["fast"]) - ema(c, p["slow"])
    d = macd - ema(macd, p["signal"])
    return (d < 0) & (d.shift(1) >= 0) & (ema(c, p["ema_len"]) > c)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    se = _short_signal(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return false, false.copy(), se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    se = _short_signal(bars_df, p)
    c = bars_df["close"]
    sl = (bars_df["high"] * (1 + p["stop_pct"] / 100) / c - 1).where(se)
    tp = (1 - bars_df["low"] * (1 - p["target_pct"] / 100) / c).where(se)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
