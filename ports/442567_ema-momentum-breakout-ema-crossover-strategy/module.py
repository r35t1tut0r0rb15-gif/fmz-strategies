"""EMA 9 / 21 crossings with an SMA 50 trend filter, 1-hour bars: the EMA 9 crossing over the EMA 21 with the close above the SMA 50 goes long, the mirror short; reversing.
Port of FMZ strategy #442567 "基于动量突破EMA交叉策略Momentum-Breakout-EMA-Crossover-Strategy" (Estrategia EMA Cruzada con Filtro de Tendencia).

FMZ source id: 442567

Source
    https://www.fmz.com/strategy/442567 (PineScript v5, FMZ last modified 2024-02-22 18:06:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 148-179), EMA 9 / 21; SMA 50
    crossover(ema9, ema21) and close > sma50 -> entry Compra;  crossunder and close < sma50 -> entry Venta

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with an SMA filter.
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

NAME = "fmz_442567_ema9_21_cross_sma50_filter_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "trend": 50}


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
    t = c.rolling(int(p["trend"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (c > t)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (c < t)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
