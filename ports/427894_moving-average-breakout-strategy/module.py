"""Heikin Ashi turn, long only, hourly bars: three green Heikin Ashi candles after a red one go long; the
position exits at a 1 % target or a 25 % stop.
Port of FMZ strategy #427894 "Moving Average Breakout Strategy" (Heikin Ashi Candle Strategy Long).

FMZ source id: 427894

Source
    https://www.fmz.com/strategy/427894 (PineScript v5, FMZ last modified 2023-09-26 16:18:37).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 167-291), validation 3, TP 1 %, SL 25 %, trail 0.2 %
    isLong = HA green on bars 0..2 and HA red 3 bars back -> entry long (qty 1, max position 1)
    exit(limit = avg price x 1.01, stop = avg price x 0.75, trail_price = trailLong)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Heikin Ashi candles of the chart's own bars (ha_close = ohlc4; ha_open = mean of the previous
      ha_open and ha_close, first (open + close) / 2).
    * Percent-of-entry levels: tp_stop 0.01, sl_stop 0.25.
    * AS WRITTEN the trail never trails: trailLong uses itself (0 at that point) instead of the 0.2 %
      input, so it is the highest close since entry, and it is passed as trail_price without a
      trail_offset, which arms no trailing stop. Not ported; decision owed for the intended trail.
    * Quantity 1 and the position cap are sizing. Long only (allow_entry_in long).
    * Stop module: portfolio_kwargs {} (driver D4).
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close entries; bracket fixed at entry.
    2 generic: PASS, candle colours and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: quantity and position cap stored; exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427894_heikin_ashi_turn_long"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "validation": [3, 2],
    "tp_pct": [1.0, 2.0],
    "sl_pct": [25.0, 5.0],
}
DEFAULT_PARAMS = {"validation": 3, "tp_pct": 1.0, "sl_pct": 25.0}


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
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    hc = (o + h + lo + c) / 4
    ho = np.empty_like(hc)
    for i in range(len(hc)):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 else (ho[i - 1] + hc[i - 1]) / 2
    green = pd.Series(hc > ho, index=bars_df.index)
    v = int(p["validation"])
    all_green = green.rolling(v).min() == 1
    red_before = ~green.shift(v, fill_value=True).astype(bool)
    long_e = (all_green & red_before).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100, "tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
