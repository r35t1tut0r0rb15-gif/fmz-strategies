"""EMA 20 / 50 crossings with a 2 % stop and a 7 % trailing stop, 10-minute bars: the fast EMA crossing over the slow one goes long, crossing under goes short, reversing; each trade is stopped at the tighter of
2 % from the entry and 7 % behind the best bar high (low for shorts).
Port of FMZ strategy #437547 "Stock Quant Trading Strategy Combining Exponential Moving Average with Trailing Stop Loss and Percentage Stop Loss" (TSL&SL%).

FMZ source id: 437547

Source
    https://www.fmz.com/strategy/437547 (PineScript v5, FMZ last modified 2024-01-03 16:25:54).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 155-253), EMA 20 / 50; trailing stop 7 %, stop loss 2 % (both sides)
    buy = crossover(ema 20, ema 50) -> entry Buy;  sell = crossunder -> entry Sell
    longTrailPrice = max(high x 0.93, previous) while long;  longLossPrice = entry x 0.98;  exit(stop = max of the two) while long;  shorts mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the tighter of a fixed 2 % stop and a 7 % trail behind the best high: the house trail
      {"type": "percent", "pct": 0.07, "anchor": "high_low"} with sl_stop 0.02 (the tighter level applies),
      mark trailing_stop. Stated approximation: the script ratchets on each bar's high at its close (the
      next bar's stop), the house trail on the best minute high up to the previous minute. REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "10min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry plus a house trail.
    2 generic: PASS, percent stop and trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the stop and trail percent inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_437547_ema_cross_pct_stop_trail"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [0.07, 0.03],
    "stop_pct": [0.02, 0.01],
}
DEFAULT_PARAMS = {"trail_pct": 0.07, "stop_pct": 0.02, "fast": 20, "slow": 50}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_pct"]),
            "trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
