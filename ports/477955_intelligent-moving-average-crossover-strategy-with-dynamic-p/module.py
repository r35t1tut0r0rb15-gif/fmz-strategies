"""SMA 7 / 40 crossings, hourly bars, long only: the cross up buys from flat with a 1 % stop and 2 % target from the entry price; the cross down closes.
Port of FMZ strategy #477955 "Intelligent Moving Average Crossover Strategy with Dynamic Profit Loss Management System" (Cruzamento de Médias Móveis (Configuração Interativa)).

FMZ source id: 477955

Source
    https://www.fmz.com/strategy/477955 (PineScript v5, FMZ last modified 2025-01-10 15:39:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 77-128), SMA 7 / 40; stop 1 %, target 2 % of strategy.position_avg_price
    crossover(sma7, sma40) and flat -> entry Compra;  every bar: exit(Compra, stop = avg x 0.99, limit = avg x 1.02);  crossunder -> close Compra

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent from the position's average price on every bar (na while flat): scalar
      fractions of the entry fill, active from the fill (as #440797). The flat test only skips a repeat,
      which the engine ignores anyway. Long only. Stop module: portfolio_kwargs {} (driver D4). No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; avg-price bracket as fractions of the fill.
    2 generic: PASS, SMA crossings with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477955_sma7_40_cross_pct_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [7, 20],
    "slow": [40, 100],
}
DEFAULT_PARAMS = {"fast": 7, "slow": 40, "sl_pct": 0.01, "tp_pct": 0.02}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    lx = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
