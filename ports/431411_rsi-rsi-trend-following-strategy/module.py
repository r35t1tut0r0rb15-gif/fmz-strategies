"""RSI 14 exits from the extremes, 1-hour bars: RSI crossing back above 30 goes long, crossing back below 70 goes short;
the source's 120-tick stop becomes an ATR fraction.
Port of FMZ strategy #431411 "基于RSI的趋势追踪策略RSI-Trend-Following-Strategy" (RSI Etoro Strategy).

FMZ source id: 431411

Source
    https://www.fmz.com/strategy/431411 (PineScript v3, FMZ last modified 2023-11-07 16:33:43).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 158-195), RSI 14, 30 / 70, stop 120 ticks
    crossover(rsi, 30) -> entry long;  crossunder(rsi, 70) -> entry short;  exit(loss = 120 ticks) per side

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the stop is 120 ticks (12 USD on BTC_USDT at mintick 0.1, about 0.08 ATR on 1-hour
      BTC); it becomes sl_atr x the Wilder ATR 14 of the signal bar, as a fraction of its close, fixed
      at entry. The date window (from Dec 2018) is dropped.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: ADAPT, tick stop -> ATR fraction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431411_rsi_extreme_exit_stop"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [14, 7],
    "sl_atr": [0.08, 1.5],
}
DEFAULT_PARAMS = {"length": 14, "over_sold": 30, "over_bought": 70, "atr_len": 14, "sl_atr": 0.08}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, int(p["length"]))
    os_, ob = float(p["over_sold"]), float(p["over_bought"])
    lg = ((r > os_) & (r.shift(1) <= os_)).astype(bool)
    sh = ((r < ob) & (r.shift(1) >= ob)).astype(bool)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return lg, sh, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lg, sh, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
