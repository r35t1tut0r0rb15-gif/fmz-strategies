"""Close crossings of the SMA 14 in the direction of the SMA 14 / 50 order, 4-hour bars: with the SMA 14 above the SMA 50 a close crossing over it goes long, below it a close crossing under goes short;
reversing (the ATR bracket re-sent from each bar is not ported).
Port of FMZ strategy #446764 "Dual Moving Average Lagging Breakout Strategy" (2MA (2 Moving Averages)).

FMZ source id: 446764

Source
    https://www.fmz.com/strategy/446764 (PineScript v4, FMZ last modified 2024-04-01 11:58:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-196), SMA 14 / 50; ATR 14 x 1.5; bracket: stop low - 1.5 ATR, target close + 2 x the stop distance (every bar)
    sma14 > sma50 and crossover(close, sma14) -> entry Buy;  sma14 < sma50 and crossunder(close, sma14) -> entry Sell
    exit(Buy, stop = low - 1.5 atr, limit = close + 2 (close - stop));  exit(Sell, mirrored)  (re-sent every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent on every bar from that bar's low / high, close and ATR, so it moves after
      entry: not ported (mark trailing_stop_pending; as #438034). Positions end at the opposite entry
      meanwhile. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "4h" from the
      backtest header (UTC-aligned 4-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket not ported (mark).
    2 generic: PASS, SMA crossings in the trend direction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the ATR bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_446764_close_sma14_cross_with_sma50_order_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [14, 20],
    "len2": [50, 100],
}
DEFAULT_PARAMS = {"len1": 14, "len2": 50}


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
    m1 = c.rolling(int(p["len1"])).mean()
    m2 = c.rolling(int(p["len2"])).mean()
    c1 = c.shift(1)
    le = (m1 > m2) & (c > m1) & (c1 <= m1.shift(1))
    se = (m1 < m2) & (c < m1) & (c1 >= m1.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
