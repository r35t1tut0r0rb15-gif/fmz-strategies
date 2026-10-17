"""RSI 14 extremes with a 1 % bracket, 1-hour bars, as written: RSI under 30 goes long, RSI above 70 goes short (reversing);
each trade carries a 1 % stop and a 1 % target. The "Fibonacci" price tests are always true.
Port of FMZ strategy #434551 "Fibonacci Retracement Reversal Strategy" (FBS Trade).

FMZ source id: 434551

Source
    https://www.fmz.com/strategy/434551 (PineScript v5, FMZ last modified 2023-12-07 15:15:26).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 143-185), RSI 14, 70 / 30; Fibonacci 0.618; TP 1 %, SL 1 %
    buy = close > low (1 - 0.618) and rsi < 30 -> entry long;  sell = close < high (1 + 0.618) and rsi > 70 -> entry short
    position long -> exit(limit = avg (1 + 1 %), stop = avg (1 - 1 %));  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * close > 0.382 x low and close < 1.618 x high hold for every bar with positive prices, so the
      signals are the RSI levels alone, as written. A signal while in the same side is ignored.
    * The bracket is fixed at the fill: sl_stop 0.01, tp_stop 0.01 (the inputs' defaults in the
      code). Pine arms it from the bar after the fill; the engine's minute stops can act within the
      fill bar (approximation stated). strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed-percent bracket.
    2 generic: PASS, RSI levels and percent exits.
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

NAME = "fmz_434551_rsi_extreme_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_len": [14, 7],
    "pct": [0.01, 0.02],
}
DEFAULT_PARAMS = {"rsi_len": 14, "fib": 0.618, "ob": 70, "os": 30, "pct": 0.01}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())
    fib = float(p["fib"])
    le = ((c > lo * (1 - fib)) & (rsi < float(p["os"]))).astype(bool)
    se = ((c < h * (1 + fib)) & (rsi > float(p["ob"])) & ~le).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["pct"]), "tp_stop": float(p["pct"])}


def portfolio_kwargs(**params):
    return {}
