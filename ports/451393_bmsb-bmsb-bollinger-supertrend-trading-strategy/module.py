"""Breaks of the bull-market support band (SMA 20 / EMA 21), 6-hour bars: the close crossing over the band's upper line goes long, crossing under its lower line goes short; reversing.
Port of FMZ strategy #451393 "BMSB-布林麦克超级趋势交易策略-BMSB-Bollinger-SuperTrend-Trading-Strategy" (BMSB Strategy Mejora (Bull Market Support Band)).

FMZ source id: 451393

Source
    https://www.fmz.com/strategy/451393 (PineScript v5, FMZ last modified 2024-05-14 15:52:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-129), SMA 20; EMA 21
    upper = max(sma20, ema21);  lower = min(sma20, ema21);  crossover(close, upper) -> close Sell, entry Buy;  crossunder(close, lower) -> close Buy, entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each close comes with the opposite entry on the same bar: one reversal. REVERSAL INTENDED. No
      sizing code. FREQ = "6h" from the backtest header (UTC-aligned 6-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, support-band breaks.
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

NAME = "fmz_451393_bmsb_band_break_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "6h"  # backtest header period: 6h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [20, 50],
    "ema_len": [21, 50],
}
DEFAULT_PARAMS = {"sma_len": 20, "ema_len": 21}


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
    sma = c.rolling(int(p["sma_len"])).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    upper = np.maximum(sma, ema)
    lower = np.minimum(sma, ema)
    c1 = c.shift(1)
    le = (c > upper) & (c1 <= upper.shift(1))
    se = (c < lower) & (c1 >= lower.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
