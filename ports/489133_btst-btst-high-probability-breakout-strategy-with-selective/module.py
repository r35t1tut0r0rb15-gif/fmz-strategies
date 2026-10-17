"""Buy-today-sell-tomorrow selection at the 15:00 bar, long only, hourly bars: on the bar opening at 15:00 (UTC, the
author's exchange clock) with a 2-3 % gain on the previous close and a bullish candle pattern (engulfing, a "morning
star" as written, or three white soldiers), not over-extended, the strategy goes long; the source's exit (a close
above the bar's own high) can never fire, so the trade is held.
Port of FMZ strategy #489133 "BTST高概率突破策略与精选股票筛选系统-BTST-High-Probability-Breakout-Strategy-with-Selective-Stock-Screening-System" (BTST Strategy).

FMZ source id: 489133

Source
    https://www.fmz.com/strategy/489133 (PineScript v5, FMZ last modified 2025-04-02 09:33:50).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 175-242), 15:00 bar, change 2-3 %, over-extension > 5 % or < -10 %
    selected = hour == 15 and minute == 0 and 2 <= (close - close[1]) / close[1] x 100 <= 3
    pattern = bullish engulfing or "morning star" (red[2], red[1], green[0], green[1] as written) or three white soldiers
    buy = pattern and selected and not over-extended -> entry long
    resistance = high on bars at minute 0 or 30;  sell = close > resistance and not over-extended -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Session open (check 9 / C6): the 15:00 test is in the chart's time zone, UTC on the author's Binance chart;
      declared as the hourly bar opening at 15:00 UTC (the name BTST suggests an Indian 15:00 IST close, which no
      UTC-aligned hourly bar opens at). The minute-0 / 30 test is always true on hourly bars.
    * The resistance is reset to the current bar's high before the breakout test, so close > resistance never holds
      and the exit never fires, as written: each long is held to the end (re-entries while long are ignored).
    * The "morning star" requires close[1] < open[1] and close[1] > open[1] at once: never true, as written.
    * Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, percentage changes and candle patterns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: the hourly bar opening at 15:00 UTC (the author's exchange clock; no DST), as the selection time.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489133_btst_1500_selection_long"
FAMILY = "calendar_seasonal"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "change_lo": [2.0, 1.0],
}
DEFAULT_PARAMS = {"hour": 15, "change_lo": 2.0, "change_hi": 3.0}


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
    o, c = bars_df["open"], bars_df["close"]
    ts = bars_df.index.tz_convert("UTC")
    at_hour = pd.Series((ts.hour == int(p["hour"])) & (ts.minute == 0), index=c.index)
    chg = (c - c.shift(1)) / c.shift(1) * 100
    selected = at_hour & (chg >= p["change_lo"]) & (chg <= p["change_hi"])
    green, red = c > o, c < o
    engulf = green & (o.shift(1) > c.shift(1)) & (c > o.shift(1)) & (o < c.shift(1))
    morning = red.shift(2, fill_value=False) & red.shift(1, fill_value=False) & green & green.shift(1, fill_value=False)
    soldiers = (green & green.shift(1, fill_value=False) & green.shift(2, fill_value=False)
                & (c > c.shift(1)) & (c.shift(1) > c.shift(2)))
    gain = (c - o) / o * 100
    over = (gain > 5) | (gain < -10)
    buy = ((engulf | morning | soldiers) & selected & ~over).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
