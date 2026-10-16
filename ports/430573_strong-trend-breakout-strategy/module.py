"""Donchian wicks, 5-minute bars, long only: a low under the 20-bar lowest of red-bar lows goes long, with a target at the
20-bar highest of green-bar highs and a 1 % stop (both re-issued from each bar in the source; fixed at the entry here).
Port of FMZ strategy #430573 "Strong Trend Breakout Strategy" (Donchian Wicks Strategy - Long Only with Customizable Donchian Exit and Stop Loss).

FMZ source id: 430573

Source
    https://www.fmz.com/strategy/430573 (PineScript v4, FMZ last modified 2023-10-30 14:53:32).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 160-191), length 20, stop 1 %
    up = close > open ? high : up[1]; down = close < open ? low : down[1]
    highest = highest(up, 20); lowest = lowest(down, 20)
    low < lowest -> entry long; exit(limit = highest) and exit(stop = close x 0.99), both re-issued every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both exits are re-issued every bar (the target follows the channel, the stop 1 % under each
      close): moving levels, rule 2, mark trailing_stop_pending. The port fixes the target at the
      signal bar's channel high (as a fraction of its close, shifted one bar) and the stop at 1 % of
      the fill. A signal whose channel high is not above its close places no target (stated).
    * Long only; a further signal while long adds nothing. Opposite entries cannot occur. Stop
      module: portfolio_kwargs {} (driver D4). FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving levels fixed at entry (rule 2).
    2 generic: PASS, channels of bar extremes and a percentage stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_430573_donchian_wicks_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "stop_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "stop_pct": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _carry(cond, val):
    out = np.zeros(len(val))
    last = 0.0
    for i in range(len(val)):
        if cond[i]:
            last = val[i]
        out[i] = last
    return out


def _channels(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    up = pd.Series(_carry((c > o).to_numpy(), h.to_numpy(dtype=float)), index=c.index)
    dn = pd.Series(_carry((c < o).to_numpy(), lo.to_numpy(dtype=float)), index=c.index)
    n = int(p["length"])
    return up.rolling(n).max(), dn.rolling(n).min()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, lowest = _channels(bars_df, p)
    long_e = (bars_df["low"] < lowest).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    highest, _ = _channels(bars_df, p)
    c = bars_df["close"]
    tp = (highest - c) / c
    tp = tp.where(tp > 0)
    return {"sl_stop": float(p["stop_pct"]) / 100, "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
