"""EMA 8 above EMA 26 with a MACD cross and a 3 % trailing stop, long only, hourly bars: from flat, EMA 8 above EMA 26
with the MACD crossing above its signal goes long; a stop 3 % under the best close since entry trails it.
Port of FMZ strategy #429497 "Dual Moving Average Monitoring Model" (Fast EMA above Slow EMA with MACD (by Coinrule)).

FMZ source id: 429497

Source
    https://www.fmz.com/strategy/429497 (PineScript v5, FMZ last modified 2023-10-17 16:33:29).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 155-197), EMA 8 / 26, MACD 12 / 26 / 9, long trail 3 %
    fastEMA > slowEMA and crossover(macd, signal) and not in a position -> entry long
    while long: longStop = max(close x (1 - 3 %), longStop[1]); exit(stop = longStop, limit = shortStopPrice = 999999)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail is ported natively (mark trailing_stop): {"type": "percent", "pct": 0.03, "anchor": "close"}.
      Stated approximation: the source ratchets 3 % under each completed bar's close (known at the next
      bar), the house under the best minute close up to the previous minute.
    * The limit is 999999 while long (the short-side default): inert. The strategy() line (with
      process_orders_on_close) is commented out: bar-close orders. The 2022 start is dropped.
    * Long only; Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: PASS, moving-average and MACD conditions, a percentage trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() stored; the trail quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_429497_ema_macd_trail_long"
FAMILY = "macd_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [3.0, 1.5],
    "slow": [26, 50],
}
DEFAULT_PARAMS = {"fast": 8, "slow": 26, "trail_pct": 3.0}


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
    e = lambda x, n: x.ewm(span=int(n), adjust=False).mean()  # noqa: E731
    macd = e(c, 12) - e(c, 26)
    sig = e(macd, 9)
    long_e = ((e(c, p["fast"]) > e(c, p["slow"])) & (macd > sig) & (macd.shift(1) <= sig.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]) / 100, "anchor": "close"}}


def portfolio_kwargs(**params):
    return {}
