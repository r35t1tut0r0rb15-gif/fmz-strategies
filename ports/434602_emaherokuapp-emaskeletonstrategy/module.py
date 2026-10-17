"""EMA 50 against the bar high, 1-hour bars, long only: the high crossing above the EMA 50 with the close above the EMA 70
goes long; the EMA crossing back above the high closes it; each trade carries a 5.1 % stop and a 9.6 % target.
Port of FMZ strategy #434602 "动态EMAherokuapp俯瞰策略EMAskeletonstrategy" (EMA+RSI Pump & Drop Swing Sniper (With Alerts & SL+TP) - Strategy).

FMZ source id: 434602

Source
    https://www.fmz.com/strategy/434602 (PineScript v4, FMZ last modified 2023-12-07 17:20:44).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 176-225), EMA 50 on close, condition source high; safety EMA 70; SL 0.051, TP 0.096 of the close in ticks; dates 2019-9999
    crossunder(ema50, high) and close > ema70 -> entry long;  crossover(ema50, high) -> close long
    exit(profit = close x 0.096 / mintick, loss = close x 0.051 / mintick)   (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-issued every bar with distances sized from the latest close, so the levels
      move after entry: stops() cannot express that (mark trailing_stop_pending). The port fixes
      them as fractions of the fill: sl_stop 0.051, tp_stop 0.096. The RSI only colours candles.
      The date window (2019 to 9999) is the author's: dropped.
    * Long only; an entry while long is ignored. Stop module: portfolio_kwargs {} (driver D4). FREQ
      = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-sized exits fixed at entry (approximation stated).
    2 generic: PASS, an average against the high and percent exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the exits quoted in original_sizing.txt.
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

NAME = "fmz_434602_ema_high_cross_bracket_long"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [50, 25],
    "safety_len": [70, 140],
}
DEFAULT_PARAMS = {"ema_len": 50, "safety_len": 70, "sl_pct": 0.051, "tp_pct": 0.096}


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
    h, c = bars_df["high"], bars_df["close"]
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["safety_len"]), adjust=False).mean()
    le = ((e < h) & (e.shift(1) >= h.shift(1)) & (c > e2)).astype(bool)
    lx = ((e > h) & (e.shift(1) <= h.shift(1))).astype(bool) & ~le
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
