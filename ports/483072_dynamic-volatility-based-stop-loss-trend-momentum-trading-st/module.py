"""MACD 12 / 26 / 9 up-crosses over the EMA 20, 2-hour bars, long only: the up-cross goes long and the MACD down-cross closes; the source's ratchet stop (highest close - 2 ATR 14 value since entry) is pending.
Port of FMZ strategy #483072 "Dynamic Volatility Based Stop Loss Trend Momentum Trading Strategy" (MACD + ATR Dynamic Stop-Loss Strategy).

FMZ source id: 483072

Source
    https://www.fmz.com/strategy/483072 (PineScript v5, FMZ last modified 2025-02-21 11:39:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-145), MACD 12 / 26 / 9; EMA 20; ATR 14; stop 1 ATR; trailing on, 2 ATR
    crossover(macd, signal) and close > ema20 -> entry Long;  crossunder(macd, signal) -> close Long
    position long -> trailingStop := max(trailingStop, close - 2 atr), stopLossLevel := trailingStop, exit(stop = stopLossLevel) re-sent every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop ratchets on the highest value of close - 2 ATR since the signal and is re-sent every bar.
      The house trail takes the best price less k ATR of the current bar (it may retreat), which is not
      this ratchet on (close - k ATR): not ported, mark trailing_stop_pending (as #440449); the MACD
      down-cross is the exit. The 1-ATR initial stop is overwritten by the trail on the first bar held.
      Long only. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the ratchet stop pending.
    2 generic: PASS, MACD crossings over an EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483072_macd_cross_over_ema20_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "macd_fast_length": [12, 8],
    "ema_length": [20, 50],
}
DEFAULT_PARAMS = {"macd_fast_length": 12, "ema_length": 20, "macd_slow_length": 26, "macd_signal": 9}


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

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    macd = ema(c, p["macd_fast_length"]) - ema(c, p["macd_slow_length"])
    sig = ema(macd, p["macd_signal"])
    e = ema(c, p["ema_length"])
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (c > e)
    lx = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
